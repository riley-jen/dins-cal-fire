# Characterizing California Wildfire Impacts Using CAL FIRE Data

This project uses CAL FIRE Damage Inspection Program (DINS) structure data and National Interagency Fire Center (NIFC/WFIGS) fire perimeter data to provide context for studies focusing on the carcinogenic effects of wildfires, such as CAFF-CRS (California Firefighter Cancer Research Study). This project's goal is to connect sampling events at the wildfire front with information about structures in the fire environment.

## Project Overview

The program focuses on six California fire incidents:

- Palisades
- Mountain
- Eaton
- Franklin
- Line
- Bridge

It combines two primary datasets:

- **CAL FIRE DINS structure data**: post-fire inspection records for structures impacted by wildland fires in the Statewide Responsibility Area. The data includes inspection locations, damage categories, structural materials, and building feature fields.
- **NIFC/WFIGS fire perimeter data**: geospatial fire perimeter records used to understand the footprint and boundary context of each incident.

The cleaned data is visualized in an interactive Matplotlib window that lets the user switch between fires and damage categories.

## What The Visualization Shows

The plotting program displays one fire at a time. For each selected fire, it shows:

- A map of inspected structures, colored by damage level.
- A fire perimeter layer over the structure map.
- A damage distribution summary.
- Sampling dates and sampling methods for that fire.
- Material composition tables for roof, siding, ground deck, and elevated deck fields.
- A stacked material bar chart.
- Building feature summaries for eaves, vent screens, window panes, patio cover/carport, fence, and combustibility.

Damage categories currently shown are:

- No damage
- Affected (>0-10%)
- Minor (10-25%)
- Major (25-50%)
- Destroyed (>50%)
- Inaccessible

Material values are grouped into categories such as asphalt, composite, masonry, metal, tile, vinyl, wood, and n/a.

## Data Filtering And Cleaning Process

The repository keeps the raw source data separate from filtered and cleaned files.

Raw input files:

- `../POSTFIRE_MASTER_DATA.geojson`
- `../WFIGS_INTERAGENCY_PERIMETERS_MASTER_DATA.geojson`

Generated working files:

- `files/POSTFIRE_FILTERED_DATA.geojson`
- `files/POSTFIRE_CLEAN_DATA.geojson`
- `files/WFIGS_INTERAGENCY_PERIMETERS_FILTERED_DATA.geojson`
- `files/WFIGS_INTERAGENCY_PERIMETERS_CLEAN_DATA.geojson`

### Filtering

The filtering scripts select only records for the six fires used in this project.

- `data/filter_structure.py` filters the CAL FIRE DINS structure dataset by `INCIDENTNAME`.
- `data/filter_perimeter.py` filters the WFIGS perimeter dataset by `poly_IncidentName`.

### Cleaning

The cleaning scripts remove records that appear inconsistent with the project scope.

- `data/clean_structure.py` keeps structure records whose `INCIDENTSTARTDATE` is within seven days of the expected incident start date.
- `data/clean_perimeter.py` keeps perimeter records that are geographically close to the Los Angeles area and whose available perimeter date fields occur after the expected incident start date.

### Reasoning

Use this space to explain why you chose the cleaning steps you did, what problems you noticed in the raw data, and what tradeoffs you made.

TODO:

- Why I selected these six fires:
- Why I used the incident-name filter:
- Why I cleaned structure records by incident start date:
- Why I cleaned perimeter records by location:
- Why I used the Los Angeles distance cutoff:
- Why I handled missing/null perimeter dates this way:
- Any limitations I noticed:

Below are the counts printed by running ```data_main.py```

--- perimeter ---
original data: 38256
filtered data: 42
clean data: 6 (time), 12 (location)
--- structure ---
original data: 132522
filtered data: 34473
clean data: 34408 (time)

## How To Use

### 1. Install dependencies

From the `dins-cal-fire` directory, create and activate a Python environment, then install the requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Regenerate filtered and cleaned files

Run the filter scripts first, then the cleaning scripts:

```bash
python3 data/filter_structure.py
python3 data/filter_perimeter.py
python3 data/clean_structure.py
python3 data/clean_perimeter.py
```

These commands read the raw GeoJSON files from the parent project directory and write updated GeoJSON files into `files/`.

### 3. Check data counts with `data_main.py`

After filtering and cleaning, run:

```bash
python3 data/data_main.py
```

This prints before-and-after counts for the structure and perimeter datasets. It is useful for checking how many records remain after each processing step.

### 4. Open the visualization with `plot_main.py`

Run:

```bash
python3 plot/plot_main.py
```

The plotting window opens with buttons for each fire. Use the fire buttons to switch incidents, and use the damage checkboxes to include or hide different damage categories. The map, pie chart, material table, material bar chart, and building feature tables update based on the selected fire and visible damage categories.

## Repository Structure

```text
dins-cal-fire/
  data/
    data_main.py
    filter_structure.py
    filter_perimeter.py
    clean_structure.py
    clean_perimeter.py
  files/
    POSTFIRE_FILTERED_DATA.geojson
    POSTFIRE_CLEAN_DATA.geojson
    WFIGS_INTERAGENCY_PERIMETERS_FILTERED_DATA.geojson
    WFIGS_INTERAGENCY_PERIMETERS_CLEAN_DATA.geojson
  plot/
    plot_main.py
    extract_structure_data.py
    extract_perimeter_data.py
    subplot/
      plot_map.py
      plot_pie.py
      plot_sampling.py
      plot_table.py
      plot_bar.py
  requirements.txt
  README.md
```

## Dependencies

The project uses Python geospatial, data analysis, and plotting libraries. Important dependencies include:

- `geopandas` for reading, writing, filtering, and projecting geospatial data.
- `shapely` for geometry handling.
- `ijson` for streaming large GeoJSON files without loading the entire raw file at once.
- `pandas` and `numpy` for table operations and data summaries.
- `matplotlib` for the interactive visualization.
- `contextily` for adding an OpenStreetMap basemap.
- `scikit-learn`, `scipy`, `rasterio`, `folium`, and related packages included in the environment for geospatial and analytical support.

The full pinned dependency list is in `requirements.txt`.

## Use Of AI

### Codex

Codex was used as a coding and documentation assistant for this project. In this README, Codex helped inspect the repository structure, summarize the purpose of the scripts, turn the project instruction PDF into background language, and draft documentation that matches the current code. Codex also identified places where the README should leave space for the project author's own cleaning logic, decision-making process, and reflection.

TODO:

- How I used Codex during coding:
- What Codex helped me debug or improve:
- How I checked Codex's suggestions:
- What parts I wrote or changed myself:

### Gemini

TODO:

- How I used Gemini:
- What Gemini helped with:
- How I checked Gemini's suggestions:

## Data Notes And Limitations

The CAL FIRE DINS dataset may include a small margin of error because severe fire damage and poor geographic access can make inspections difficult. Null values indicate information that could not be determined in the field. DINS records also include both field-determined address fields and address/APN fields added later through spatial joins.

The WFIGS perimeter dataset may not provide daily perimeter updates for every incident. Some fires may have only limited perimeter records or a final unified perimeter. The current plotting code uses the first cleaned perimeter record available for each fire.

## Author Notes
Please email me if you have questions:
Riley Jen
rileykjen@gmail.com | 415-300-0824

June 2026 - July 2026
