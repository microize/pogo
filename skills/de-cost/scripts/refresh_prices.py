#!/usr/bin/env python3
"""Refresh the static Azure Databricks price file used by the de-cost skill.

Sources (both public, no credentials):
  1. Azure Retail Prices API (official): DBU rate per workload SKU and Linux pay-as-you-go VM prices.
     https://prices.azure.com/api/retail/prices
  2. Azure pricing calculator feed for Azure Databricks (unofficial, the data behind the public calculator page):
     DBUs per hour per node type, Photon multiplier, cores, RAM, SQL warehouse sizes, serverless pipeline rate.
     https://azure.microsoft.com/api/v3/pricing/databricks/calculator/

Usage (needs outbound internet; run from a notebook cell in the skills repo's Git folder):
  %sh python skills/de-cost/scripts/refresh_prices.py --region eastus2 [--tier premium] [--out skills/de-cost/references/prices]
Writes azure-<region>.json (machine-readable) and azure-<region>.md (readable table) next to each other.
List prices only: pay-as-you-go, USD, no commit discounts, no reservations, no taxes.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request

RETAIL = "https://prices.azure.com/api/retail/prices"
CALC = "https://azure.microsoft.com/api/v3/pricing/databricks/calculator/?culture=en-us&discount=mosp"
UA = {"User-Agent": "genie-de-skills/de-cost price refresh"}

# workload key -> retail meterName (tier prefix added at runtime)
WORKLOADS = {
    "jobs": "Jobs Compute DBU",
    "jobs_photon": "Jobs Compute Photon DBU",
    "jobs_light": "Jobs Light Compute DBU",
    "all_purpose": "All-purpose Compute DBU",
    "all_purpose_photon": "All-Purpose Photon DBU",
    "pipeline_core": "Core Compute Delta Live Tables DBU",
    "pipeline_pro": "Pro Compute Delta Live Tables DBU",
    "pipeline_advanced": "Advanced Compute Delta Live Tables DBU",
    "pipeline_core_photon": "Core Compute Photon Delta Live Tables DBU",
    "pipeline_pro_photon": "Pro Compute Photon Delta Live Tables DBU",
    "pipeline_advanced_photon": "Advanced Compute Photon Delta Live Tables DBU",
    "sql_classic": "SQL Analytics DBU",
    "sql_pro": "SQL Compute Pro DBU",
    "sql_serverless": "Serverless SQL DBU",
    "serverless_jobs": "Automated Serverless Compute DBU",
    "serverless_notebooks": "Interactive Serverless Compute DBU",
    "serverless_database": "Database Serverless Compute DBU",
    "model_training": "Model Training DBU",
}

# common classic node types to keep in the static file (calculator slugs); extend with --nodes
DEFAULT_NODES = [
    "ds3v2", "ds4v2", "ds5v2", "d4dsv4", "d8dsv4", "d16dsv4", "d4dsv5", "d8dsv5", "d16dsv5", "d4adsv5", "d8adsv5",
    "e4dsv4", "e8dsv4", "e16dsv4", "e4dsv5", "e8dsv5", "e16dsv5", "f4s", "f8s", "f16s", "l8sv3", "l16sv3",
]


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode("utf-8"))


def retail(filter_expr):
    url = RETAIL + "?" + urllib.parse.urlencode({"$filter": filter_expr})
    items = []
    while url:
        d = get_json(url)
        items += d.get("Items", [])
        url = d.get("NextPageLink")
    return items


def slug_to_arm(slug):
    """d4dsv4 -> Standard_D4ds_v4, ds3v2 -> Standard_DS3_v2, f4s -> Standard_F4s."""
    m = re.match(r"^([a-z]+)(\d+)([a-z]*?)(?:v(\d+))?$", slug)
    if not m:
        return None
    fam, num, suf, ver = m.groups()
    name = f"Standard_{fam.upper()}{num}{suf}"
    return name + (f"_v{ver}" if ver else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default="eastus2", help="Azure armRegionName, e.g. eastus2, westeurope")
    ap.add_argument("--tier", default="premium", choices=["premium", "standard"])
    ap.add_argument("--nodes", default="", help="extra calculator node slugs, comma separated (e.g. d32dsv5)")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "prices"))
    a = ap.parse_args()
    tier = a.tier.capitalize()
    region = a.region.lower()
    calc_region = None

    # 1. DBU rates (official)
    dbx = retail(f"serviceName eq 'Azure Databricks' and armRegionName eq '{region}' and priceType eq 'Consumption'")
    by_meter = {i["meterName"]: i for i in dbx}
    rates, missing = {}, []
    for key, meter in WORKLOADS.items():
        it = by_meter.get(f"{tier} {meter}")
        if it and it["unitPrice"] > 0:
            rates[key] = {"usd_per_dbu": it["unitPrice"], "meter": it["meterName"], "sku": it["skuName"]}
        else:
            missing.append(key)

    # 2. calculator feed (DBU per node, warehouse sizes, serverless pipeline rate)
    calc = get_json(CALC)
    offers = calc.get("offers", {})
    # map retail region name to calculator region slug, e.g. eastus2 -> us-east-2
    sample = next(iter(offers.values()))["prices"]["perhour"] if offers else {}
    cand = [k for k in sample if k.replace("-", "") in (region, region.replace("us", "us"))]
    alias = {"eastus": "us-east", "eastus2": "us-east-2", "westus": "us-west", "westus2": "us-west-2", "westus3": "us-west-3",
             "centralus": "us-central", "northeurope": "europe-north", "westeurope": "europe-west",
             "uksouth": "united-kingdom-south", "southeastasia": "asia-pacific-southeast", "centralindia": "central-india",
             "australiaeast": "australia-east"}
    calc_region = alias.get(region) or (cand[0] if cand else None)

    nodes = {}
    wanted = DEFAULT_NODES + [n.strip() for n in a.nodes.split(",") if n.strip()]
    for slug in wanted:
        o = offers.get(f"jobs-compute-{slug}-{a.tier}")
        if not o or "dbuCount" not in o:
            continue
        nodes[slug] = {"arm_sku": slug_to_arm(slug), "dbu_per_hour": o["dbuCount"],
                       "photon_dbu_multiplier": o.get("photonDbuMultiplier", 1.0),
                       "vcpu": o.get("cores"), "ram_gb": o.get("ram")}

    # 3. VM prices (official), Linux pay-as-you-go, not Spot / Low Priority
    for slug, n in nodes.items():
        if not n["arm_sku"]:
            continue
        vm = retail(f"serviceName eq 'Virtual Machines' and armRegionName eq '{region}' and armSkuName eq '{n['arm_sku']}' and priceType eq 'Consumption'")
        lin = [i for i in vm if "Windows" not in i["productName"] and "Spot" not in i["skuName"] and "Low Priority" not in i["skuName"]]
        n["vm_usd_per_hour"] = lin[0]["unitPrice"] if lin else None

    sql_sizes = {}
    for s in calc.get("dataBricksSqlProClusterInstances", []):
        m = re.search(r"([\d.]+) Database Units", s.get("displayName", ""))
        if m:
            sql_sizes[s["slug"]] = {"display": s["displayName"].split(",")[0], "dbu_per_hour": float(m.group(1))}

    serverless_pipeline = None
    lf = offers.get("lakeflow-serverless-compute")
    if lf and calc_region:
        v = lf["prices"]["perhour"].get(calc_region)
        if v:
            serverless_pipeline = {"usd_per_dbu": v["value"], "source": "calculator feed (lakeflow-serverless-compute)"}
    if serverless_pipeline:
        rates["serverless_pipelines"] = serverless_pipeline
    elif "serverless_pipelines" not in rates:
        missing.append("serverless_pipelines")

    out = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "region": region, "calculator_region": calc_region, "tier": a.tier, "currency": "USD",
        "basis": "list price, pay-as-you-go, no commit discount, no reservations, no taxes",
        "sources": [RETAIL, CALC],
        "dbu_rates": rates, "missing_rates": missing,
        "classic_nodes": nodes, "sql_warehouse_sizes": sql_sizes,
        "formulas": {
            "classic": "hours * nodes * (dbu_per_hour * photon_mult * usd_per_dbu[workload] + vm_usd_per_hour)",
            "sql_warehouse_pro_or_classic": "hours * size_dbu * usd_per_dbu[sql_pro|sql_classic] (+ VM cost billed by Azure for classic/pro)",
            "sql_serverless": "hours * size_dbu * usd_per_dbu[sql_serverless] (VM included)",
            "serverless_jobs_or_pipelines": "dbus_consumed * usd_per_dbu[serverless_*] (VM included; dbus from system.billing.usage or an estimate)",
        },
    }
    os.makedirs(a.out, exist_ok=True)
    jp = os.path.join(a.out, f"azure-{region}.json")
    with open(jp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
    md = [f"# Azure Databricks list prices: {region} ({a.tier})", "",
          f"Generated {out['generated_at']} by refresh_prices.py. {out['basis']}. Sources: Azure Retail Prices API, Azure calculator feed.", "",
          "## DBU rates (USD per DBU)", "", "| Workload | USD/DBU | Meter |", "|---|---|---|"]
    md += [f"| {k} | {v['usd_per_dbu']} | {v.get('meter', v.get('source'))} |" for k, v in rates.items()]
    md += ["", "## Classic node types", "", "| Node | Azure SKU | vCPU | RAM GB | DBU/h | Photon x | VM USD/h |", "|---|---|---|---|---|---|---|"]
    md += [f"| {s} | {n['arm_sku']} | {n['vcpu']} | {n['ram_gb']} | {n['dbu_per_hour']} | {n['photon_dbu_multiplier']} | {n.get('vm_usd_per_hour')} |" for s, n in nodes.items()]
    md += ["", "## SQL warehouse sizes", "", "| Size | DBU/h |", "|---|---|"]
    md += [f"| {v['display']} | {v['dbu_per_hour']} |" for v in sql_sizes.values()]
    if missing:
        md += ["", f"Missing rates (not published for this region or tier): {', '.join(missing)}"]
    with open(os.path.join(a.out, f"azure-{region}.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md) + "\n")
    print(f"wrote {jp} ({len(rates)} rates, {len(nodes)} node types, {len(sql_sizes)} warehouse sizes); missing: {missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
