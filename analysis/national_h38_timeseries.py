#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
national_h38_timeseries.py

Computes the national annual H38 and H46 time series for Kenya (1991-2025)
from ERA5-HEAT monthly UTCI netCDF files, using an area-averaged approach
across all grid cells within Kenya's administrative boundary.

This script produces:
  - panel_national_annual_1991_2025.csv
  - panel_national_monthly_1991_2025.csv

Method:
  National annual mean H38 (and H46) is computed as the arithmetic mean of
  annual grid-cell totals across all ERA5-HEAT grid cells falling within
  Kenya's administrative boundary (n = 749 cells at ~0.25 deg resolution).
  This is equivalent to an area-averaged national metric; it is NOT
  population-weighted.

  Annual anomalies are computed relative to the 1991-2020 WMO climatological
  baseline mean.

Data requirements:
  - ERA5-HEAT monthly UTCI statistics netCDF files (Copernicus CDS)
    Variable used: utci_days_above_38_daily_max, utci_days_above_46_daily_max
  - Kenya administrative boundary GeoJSON (geoBoundaries ADM2, 290 subcounties)

Usage (Google Colab):
  1. Upload UTCI_1991_2025_monthly.zip and All_admins_joined.geojson
  2. Unzip the UTCI archive
  3. Run this script

Author: Felix Oluoch
Date: March 2026
"""

import os
import glob
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
from shapely.geometry import Point

# ============================================================
# CONFIGURATION - update paths for your environment
# ============================================================
UTCI_DIR = "UTCI_1991_2025_monthly"          # directory containing monthly .nc files
BOUNDARY_FILE = "All_admins_joined.geojson"   # Kenya ADM2 boundaries
OUTPUT_DIR = "."                               # output directory for CSVs
YEARS = range(1991, 2026)
BASELINE_START = 1991
BASELINE_END = 2020

# H38 and H46 variable names in the ERA5-HEAT monthly product
H38_VAR = "utci_days_above_38_daily_max"
H46_VAR = "utci_days_above_46_daily_max"


def build_kenya_mask(boundary_file, lat, lon):
    """
    Build a boolean mask identifying ERA5-HEAT grid cells that fall within
    Kenya's administrative boundary.

    Parameters
    ----------
    boundary_file : str
        Path to Kenya ADM2 GeoJSON boundary file.
    lat : array
        Latitude coordinates from the ERA5-HEAT grid.
    lon : array
        Longitude coordinates from the ERA5-HEAT grid.

    Returns
    -------
    mask : np.ndarray, shape (len(lat), len(lon)), dtype bool
        True for grid cells inside Kenya.
    n_cells : int
        Number of grid cells inside Kenya.
    """
    gdf = gpd.read_file(boundary_file)
    kenya_union = gdf.union_all()

    mask = np.zeros((len(lat), len(lon)), dtype=bool)
    for i, la in enumerate(lat):
        for j, lo in enumerate(lon):
            mask[i, j] = kenya_union.contains(Point(lo, la))

    n_cells = int(mask.sum())
    print(f"Kenya grid mask: {n_cells} cells inside boundary "
          f"(of {len(lat)} x {len(lon)} = {len(lat)*len(lon)} total)")
    return mask, n_cells


def compute_annual_national_timeseries(utci_dir, mask, lat, lon, years):
    """
    Compute annual national H38 and H46 values as the arithmetic mean
    across all ERA5-HEAT grid cells within Kenya.

    For each year, monthly H38 (and H46) grids are summed to produce an
    annual total per grid cell. The national value is the unweighted mean
    across all masked (Kenya) grid cells.

    Parameters
    ----------
    utci_dir : str
        Path to directory containing monthly UTCI netCDF files.
    mask : np.ndarray
        Boolean mask for Kenya grid cells.
    lat, lon : arrays
        Grid coordinates.
    years : iterable of int
        Years to process.

    Returns
    -------
    annual_df : pd.DataFrame
        Columns: year, H38_national_mean_days_per_year,
                 H46_national_mean_days_per_year
    monthly_df : pd.DataFrame
        Columns: year, month, H38_mean_days_in_month,
                 H46_mean_days_in_month
    """
    annual_rows = []
    monthly_rows = []

    for year in years:
        annual_h38 = np.zeros((len(lat), len(lon)))
        annual_h46 = np.zeros((len(lat), len(lon)))

        for month in range(1, 13):
            pattern = os.path.join(utci_dir, f"*{year}{month:02d}*")
            files = glob.glob(pattern)
            if not files:
                print(f"  WARNING: missing file for {year}-{month:02d}")
                continue

            ds = xr.open_dataset(files[0])
            h38_grid = ds[H38_VAR].values[0]   # shape: (lat, lon)
            h46_grid = ds[H46_VAR].values[0]
            ds.close()

            # Accumulate annual totals
            annual_h38 += np.nan_to_num(h38_grid)
            annual_h46 += np.nan_to_num(h46_grid)

            # Monthly national mean (area-averaged)
            h38_monthly_mean = np.nan_to_num(h38_grid)[mask].mean()
            h46_monthly_mean = np.nan_to_num(h46_grid)[mask].mean()
            monthly_rows.append({
                "year": year,
                "month": month,
                "H38_mean_days_in_month": round(float(h38_monthly_mean), 4),
                "H46_mean_days_in_month": round(float(h46_monthly_mean), 6),
            })

        # Annual national mean (area-averaged across Kenya grid cells)
        h38_annual_mean = float(annual_h38[mask].mean())
        h46_annual_mean = float(annual_h46[mask].mean())

        annual_rows.append({
            "year": year,
            "H38_national_mean_days_per_year": round(h38_annual_mean, 4),
            "H46_national_mean_days_per_year": round(h46_annual_mean, 6),
        })
        print(f"  {year}: H38 = {h38_annual_mean:.1f}, H46 = {h46_annual_mean:.3f}")

    annual_df = pd.DataFrame(annual_rows)
    monthly_df = pd.DataFrame(monthly_rows)
    return annual_df, monthly_df


def add_anomalies(annual_df, baseline_start, baseline_end):
    """
    Add anomaly columns relative to the WMO climatological baseline.

    Parameters
    ----------
    annual_df : pd.DataFrame
        Must contain year, H38_national_mean_days_per_year,
        H46_national_mean_days_per_year.
    baseline_start, baseline_end : int
        Start and end years for the baseline period (inclusive).

    Returns
    -------
    annual_df : pd.DataFrame
        With added columns: H38_baseline_mean_1991_2020,
        H46_baseline_mean_1991_2020, H38_anomaly_vs_1991_2020_days,
        H46_anomaly_vs_1991_2020_days
    """
    baseline = annual_df[
        (annual_df["year"] >= baseline_start) &
        (annual_df["year"] <= baseline_end)
    ]
    h38_baseline = baseline["H38_national_mean_days_per_year"].mean()
    h46_baseline = baseline["H46_national_mean_days_per_year"].mean()

    annual_df["H38_baseline_mean_1991_2020"] = round(h38_baseline, 4)
    annual_df["H46_baseline_mean_1991_2020"] = round(h46_baseline, 6)
    annual_df["H38_anomaly_vs_1991_2020_days"] = round(
        annual_df["H38_national_mean_days_per_year"] - h38_baseline, 4
    )
    annual_df["H46_anomaly_vs_1991_2020_days"] = round(
        annual_df["H46_national_mean_days_per_year"] - h46_baseline, 6
    )

    print(f"\nBaseline (1991-2020):")
    print(f"  H38 = {h38_baseline:.2f} days/year")
    print(f"  H46 = {h46_baseline:.4f} days/year")
    return annual_df


def main():
    print("=" * 60)
    print("National H38/H46 Time Series: Area-Averaged")
    print("ERA5-HEAT UTCI, Kenya 1991-2025")
    print("=" * 60)

    # Load grid coordinates from any netCDF file
    sample_file = glob.glob(os.path.join(UTCI_DIR, "*.nc"))[0]
    ds = xr.open_dataset(sample_file)
    lat = ds.lat.values
    lon = ds.lon.values
    ds.close()
    print(f"Grid: {len(lat)} lat x {len(lon)} lon")

    # Build Kenya mask
    print("\nBuilding Kenya boundary mask...")
    mask, n_cells = build_kenya_mask(BOUNDARY_FILE, lat, lon)

    # Compute time series
    print("\nComputing annual and monthly national means...")
    annual_df, monthly_df = compute_annual_national_timeseries(
        UTCI_DIR, mask, lat, lon, YEARS
    )

    # Add anomalies
    annual_df = add_anomalies(annual_df, BASELINE_START, BASELINE_END)

    # Save outputs
    annual_path = os.path.join(OUTPUT_DIR, "panel_national_annual_1991_2025.csv")
    monthly_path = os.path.join(OUTPUT_DIR, "panel_national_monthly_1991_2025.csv")

    annual_df.to_csv(annual_path, index=False)
    monthly_df.to_csv(monthly_path, index=False)

    print(f"\nOutputs saved:")
    print(f"  {annual_path} ({len(annual_df)} rows)")
    print(f"  {monthly_path} ({len(monthly_df)} rows)")

    # Summary statistics
    print(f"\nKey values:")
    for yr in [1999, 2018, 2024, 2025]:
        row = annual_df[annual_df["year"] == yr].iloc[0]
        print(f"  {yr}: H38 = {row['H38_national_mean_days_per_year']:.1f}, "
              f"anomaly = {row['H38_anomaly_vs_1991_2020_days']:+.1f}")


if __name__ == "__main__":
    main()
