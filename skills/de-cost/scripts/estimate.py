#!/usr/bin/env python3
"""Compare the cost and run time of compute options from the static price file (de-cost skill).

Usage:
  python estimate.py --prices ../references/prices/azure-eastus2.json --scenario scenario.json
Scenario JSON:
  {"runs_per_month": 30,
   "options": [
     {"name": "classic pipeline", "kind": "classic", "workload": "pipeline_advanced", "node": "d4dsv4",
      "nodes": 2, "run_minutes": 4, "startup_minutes": 7, "photon": false},
     {"name": "serverless pipeline", "kind": "serverless", "workload": "serverless_pipelines",
      "dbus_per_run": 0.6, "run_minutes": 3, "startup_minutes": 0.5},
     {"name": "SQL warehouse 2XS", "kind": "sql", "workload": "sql_serverless", "size": "twoxsmall",
      "run_minutes": 5, "startup_minutes": 0.2}]}
Billed time = startup + run (+ idle shutdown delay if given as idle_minutes). List prices only.
"""
import argparse
import json
import sys


def cost(o, p):
    rate = p["dbu_rates"][o["workload"]]["usd_per_dbu"]
    billed_h = (o.get("startup_minutes", 0) + o["run_minutes"] + o.get("idle_minutes", 0)) / 60.0
    if o["kind"] == "classic":
        n = p["classic_nodes"][o["node"]]
        mult = n["photon_dbu_multiplier"] if o.get("photon") else 1.0
        dbu = billed_h * o["nodes"] * n["dbu_per_hour"] * mult
        vm = billed_h * o["nodes"] * (n.get("vm_usd_per_hour") or 0)
        return dbu, dbu * rate + vm, vm
    if o["kind"] == "sql":
        dbu = billed_h * p["sql_warehouse_sizes"][o["size"]]["dbu_per_hour"]
        return dbu, dbu * rate, 0.0
    if o["kind"] == "serverless":
        dbu = o["dbus_per_run"]
        return dbu, dbu * rate, 0.0
    raise ValueError(o["kind"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prices", required=True)
    ap.add_argument("--scenario", required=True)
    a = ap.parse_args()
    p = json.load(open(a.prices, encoding="utf-8"))
    s = json.load(open(a.scenario, encoding="utf-8"))
    runs = s.get("runs_per_month", 30)
    print(f"Prices: {p['region']} {p['tier']} generated {p['generated_at']} ({p['basis']})")
    print("| Option | Wall time per run (min) | DBU per run | USD per run | of which VM | USD per month |")
    print("|---|---|---|---|---|---|")
    for o in s["options"]:
        dbu, usd, vm = cost(o, p)
        wall = o.get("startup_minutes", 0) + o["run_minutes"]
        print(f"| {o['name']} | {wall:.1f} | {dbu:.2f} | {usd:.3f} | {vm:.3f} | {usd * runs:.2f} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
