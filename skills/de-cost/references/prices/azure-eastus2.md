# Azure Databricks list prices: eastus2 (premium)

Generated 2026-11-11T06:43:54+00:00 by refresh_prices.py. list price, pay-as-you-go, no commit discount, no reservations, no taxes. Sources: Azure Retail Prices API, Azure calculator feed.

## DBU rates (USD per DBU)

| Workload | USD/DBU | Meter |
|---|---|---|
| jobs | 0.3 | Premium Jobs Compute DBU |
| jobs_photon | 0.3 | Premium Jobs Compute Photon DBU |
| jobs_light | 0.22 | Premium Jobs Light Compute DBU |
| all_purpose | 0.55 | Premium All-purpose Compute DBU |
| all_purpose_photon | 0.55 | Premium All-Purpose Photon DBU |
| pipeline_core | 0.3 | Premium Core Compute Delta Live Tables DBU |
| pipeline_pro | 0.38 | Premium Pro Compute Delta Live Tables DBU |
| pipeline_advanced | 0.54 | Premium Advanced Compute Delta Live Tables DBU |
| pipeline_core_photon | 0.3 | Premium Core Compute Photon Delta Live Tables DBU |
| pipeline_pro_photon | 0.38 | Premium Pro Compute Photon Delta Live Tables DBU |
| pipeline_advanced_photon | 0.54 | Premium Advanced Compute Photon Delta Live Tables DBU |
| sql_classic | 0.22 | Premium SQL Analytics DBU |
| sql_pro | 0.55 | Premium SQL Compute Pro DBU |
| sql_serverless | 0.7 | Premium Serverless SQL DBU |
| serverless_jobs | 0.45 | Premium Automated Serverless Compute DBU |
| serverless_notebooks | 0.95 | Premium Interactive Serverless Compute DBU |
| serverless_database | 0.26 | Premium Database Serverless Compute DBU |
| model_training | 0.65 | Premium Model Training DBU |
| serverless_pipelines | 0.45 | calculator feed (lakeflow-serverless-compute) |

## Classic node types

| Node | Azure SKU | vCPU | RAM GB | DBU/h | Photon x | VM USD/h |
|---|---|---|---|---|---|---|
| d4dsv4 | Standard_D4ds_v4 | 4 | 16.0 | 0.75 | 2.5 | 0.226 |
| d8dsv4 | Standard_D8ds_v4 | 8 | 32.0 | 1.5 | 2.5 | 0.452 |
| d16dsv4 | Standard_D16ds_v4 | 16 | 64.0 | 3.0 | 2.5 | 0.904 |
| d4dsv5 | Standard_D4ds_v5 | 4 | 16.0 | 1.0 | 2.5 | 0.226 |
| d8dsv5 | Standard_D8ds_v5 | 8 | 32.0 | 2.0 | 2.5 | 0.452 |
| d16dsv5 | Standard_D16ds_v5 | 16 | 64.0 | 4.0 | 2.5 | 0.904 |
| e4dsv4 | Standard_E4ds_v4 | 4 | 32.0 | 1.0 | 2.5 | 0.288 |
| e8dsv4 | Standard_E8ds_v4 | 8 | 64.0 | 2.0 | 2.5 | 0.576 |
| e16dsv4 | Standard_E16ds_v4 | 16 | 128.0 | 4.0 | 2.5 | 1.152 |
| e4dsv5 | Standard_E4ds_v5 | 4 | 32.0 | 1.5 | 2.5 | 0.288 |
| e8dsv5 | Standard_E8ds_v5 | 8 | 64.0 | 2.75 | 2.5 | 0.576 |
| e16dsv5 | Standard_E16ds_v5 | 16 | 128.0 | 5.5 | 2.5 | 1.152 |
| l8sv3 | Standard_L8s_v3 | 8 | 64.0 | 2.75 | 2.5 | 0.698 |
| l16sv3 | Standard_L16s_v3 | 16 | 128.0 | 5.5 | 2.5 | 1.396 |

## SQL warehouse sizes

| Size | DBU/h |
|---|---|
| 2X-Small | 4.0 |
| X-Small | 6.0 |
| Small | 12.0 |
| Medium | 24.0 |
| Large | 40.0 |
| X-Large | 80.0 |
| 2X-Large | 144.0 |
| 3X-Large | 272.0 |
| 4X-Large | 528.0 |
