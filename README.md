# Library isochrones

This repository contains code to generate library isochrones from [Open Route Service](https://openrouteservice.org/).

## Introduction

An isochrone is a line on a map that connects points that can be reached within a certain limit (e.g. time or distance). In this case, the isochrones are generated from points on the map that represent libraries.

Isochrones are useful for understanding the accessibility of a location as well as understanding the people within those limits. It differs from more crude measures of accessibility such as the 'straight line' distance between two points. In the case of libraries, and other public service points, isochrones can be useful for defining catchment areas, understanding the population within those areas, and planning services.

## Scripts

Scripts for different library data sources are stored in the `scripts` folder. The scripts are written in Python and use the `openrouteservice` library to generate isochrones.

| Script                  | Description                                                             |
| ----------------------- | ----------------------------------------------------------------------- |
| `basic_dataset_2023.py` | Script to generate isochrones from the Arts Council basic dataset 2023. |

To run the scripts change to the scripts directory and run the relevant script with python (3)

```console
cd scripts
python basic_dataset_2023.py
```

```console
ogr2ogr -f "CSV" .\data\isochrones\basic-dataset-2023\basic-dataset-2023.csv .\data\isochrones\basic-dataset-2023\basic-dataset-2023.geojson -lco GEOMETRY=AS_WKT
```

## Data

The data is stored in the `data` folder and is generated using python scripts.

Current data includes:

| File/Folder                                     | Description                                                 |
| ----------------------------------------------- | ----------------------------------------------------------- |
| `basic-dataset-for-libraries-2023-enhanced.csv` | Enhanced version of the Arts Council 2023 libraries dataset |
| `isochrones/basic-dataset-2023`                 | Folder for the Arts Council 2023 libraries dataset          |
| `isochrones/basic-dataset-2023/locations.csv`   | CSV file with data from the generated isochrones            |

## License

This repository is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
