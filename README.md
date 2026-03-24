# kenya-subcounty-heat-hvi
# Thirty-Five Years of Accelerating Heat Stress in Kenya

**Subnational Hazard, Exposure Burden, and Vulnerability in Priority Populations**

Felix Oluoch¹² · Fredrick Gudda¹²

¹ Department of Population Health, Aga Khan University, Nairobi, Kenya  
² Institute for Global Health and Development, Aga Khan University, East Africa

---

## Overview

This repository contains the analysis code supporting the manuscript:

> *Thirty-Five Years of Accelerating Heat Stress in Kenya: Subnational Hazard, Exposure Burden, And Vulnerability in Priority Populations*

We conducted a nationwide ecological panel study characterising heat hazard, exposure burden, and heat vulnerability across all 290 sub-counties of Kenya, focusing on **pregnant women**, **children under five**, and **adults aged 60 and older** (2015–2025), with extended climatological context from 1991 to 2025.

---

## Key Findings

- National population-weighted mean days exceeding 38°C (H38) increased significantly from 1991–2025 (Sen slope 0.97 days/year; *p* < 0.001), with record levels in 2024 and 2025.
- 61 sub-counties with sustained heat (≥30 days/year) account for ~96% of annual heat exposure burden across all priority groups.
- Heat exposure is **inversely associated with relative wealth** (Spearman ρ = −0.561; *p* < 0.001).
- Heat Vulnerability Index (HVI) rankings are highly concordant for pregnant women and children under five (ρ = 0.977), with older adults showing additional priority in coastal transitional sub-counties.

---

## Repository Structure

```
climate-hvi-kenya/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
└── analysis/
    └── climate_hvi_kenya.py   # Main Google Earth Engine analysis script
```

---

## Data Sources

| Dataset | Description | Source |
|---|---|---|
| ERA5-HEAT (Copernicus) | Universal Thermal Climate Index (UTCI); H38 & H46 metrics | Copernicus Climate Data Store |
| WorldPop Age-Sex | Gridded population by age/sex, 100m resolution, 2015–2030 | `projects/sat-io/open-datasets/WORLDPOP/agesex` |
| geoBoundaries ADM0/1/2 | Kenya administrative boundaries (sub-county level) | `WM/geoLab/geoBoundaries/600` |
| Relative Wealth Index | Socioeconomic vulnerability proxy | Meta / Data for Good |

---

## Analysis Script

The script [`analysis/climate_hvi_kenya.py`](analysis/climate_hvi_kenya.py) was developed in Google Colab using the **Google Earth Engine Python API** and covers:

- Extraction of age-stratified population denominators (elderly 60+, children 0–4, infants, women of reproductive age) per sub-county per year
- Calibration of estimated annual births and pregnancies using national anchor-year data
- Computation of sub-county WRA shares and interpolated calibration factors (κ and r)
- Export of zonal statistics as CSV and administrative boundaries as GeoJSON

### Running the Script

The script requires a Google Earth Engine account. To run:

```bash
# 1. Install dependencies
pip install earthengine-api pandas numpy openpyxl

# 2. Authenticate with Earth Engine
earthengine authenticate

# 3. Run in Google Colab or a local environment
#    Update the project ID (currently "ee-felixoluoch") to your own GEE project
python analysis/climate_hvi_kenya.py
```

> **Note:** Replace `ee-felixoluoch` with your own Google Earth Engine project ID before running.

---

## Outputs

The script generates the following CSV files:

| File | Description |
|---|---|
| `kenya_adm2_60plus_population_2015-2030.csv` | Total/female/male 60+ population per sub-county per year |
| `kenya_adm2_0_4_population_2015-2030.csv` | Total/female/male 0–4 population per sub-county per year |
| `kenya_adm2_infants_2015-2030.csv` | Infant (0–12 months) population per sub-county per year |
| `kenya_adm2_wra_2015-2030.csv` | Women of reproductive age (15–49) per sub-county per year |
| `kenya_subcounty_population_and_events_2015-2030.csv` | Combined: infants, WRA, estimated births & pregnancies |
| `kenya_adm2_boundaries_indexed.geojson` | ADM2 boundaries with `object_id` property |

---

## Citation

*Manuscript under review. Citation details will be updated upon publication.*

---
## Archive

The first archived release of this repository is available on Zenodo:

DOI:[doi.org/10.5281/zenodo.19200614](https://doi.org/10.5281/zenodo.19201792)

If you use this repository, please cite the Zenodo record associated with the release.

## Contact

**Dr Felix Oluoch**, PhD, MPH  
Department of Population Health, Aga Khan University, Nairobi, Kenya  
Institute for Global Health and Development, Aga Khan University, East Africa  
📧 oluoch.felix@aku.edu

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
