# Library isochrones

This repository contains code to generate library isochrones from [Open Route Service](https://openrouteservice.org/).

An isochrone is a line on a map that connects points that can be reached within a certain limit (e.g. time or distance). In this case, the isochrones are generated from a set of libraries in the UK.

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
