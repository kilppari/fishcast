# Fishcaster
Forecaster for best fishing hours based on weather forecast and moon phases.

The algorithm used in this script is described in the book **Kalastuksen taito: 
olosuhteet, vieheet, kohteet** by **Tom Berg**. 
(ISBN: 978-952-266-800-4)

This script works for Finnish locations only and is not suitable for other regions.

## Description
Calculates optimal fishing times using weather forecasts from the Finnish Meteorological Institute (FMI) and moon phase data. 
Considered factors are:
- Air pressure changes
- Wind direction
- Moon phases
- Sea level changes (optional)

## Prerequisites
- Python 3.x
- Required packages: `requests`, `ephem`, `pytz`

## Installation
```bash
pip install requests ephem pytz
```
## Usage
Basic example to get forecast of Helsinki for next 24 hours
```bash
python fishcast.py -l Helsinki -hr 24
```

### Arguments
- `--location`, `-l`: Location in Finland (default: Oulu)
- `--hours`, `-hr`: Number of forecast hours (default: 48)
- `--timezone`, `-tz`: Timezone (default: Europe/Helsinki)
- `--visualize`, `-v`: Visualize the hourly forecast in ASCII chart (default: False)
- `--sealevel`, `-sl`: Location for sealevel measurement (default: None). Do not use if not fishing in sea.

```bash
python fishcast.py --help
usage: fishcast.py [-h] [--timezone TIMEZONE] [--location LOCATION] [--hours HOURS] [--visualize] [--sealevel SEALEVEL]

Calculate fishing forecast based on weather and moon data.

options:
  -h, --help            show this help message and exit
  --timezone TIMEZONE, -tz TIMEZONE
                        Timezone (default: Europe/Helsinki)
  --location LOCATION, -l LOCATION
                        Location in Finland (default: Oulu)
  --hours HOURS, -hr HOURS
                        Forecast hours (default: 48)
  --visualize, -v       Visualize the forecast (default: OFF)
  --sealevel SEALEVEL, -sl SEALEVEL
                        Location for sealevel measurement (default: OFF) Possible values: Pietarsaari, Kemi, Porvoo, Vaasa, Turku, Rauma, Raahe, Oulu, Mantyluoto,      
                        Kaskinen, Helsinki, Hanko, Hamina, Degerby
```	

## Output
The script provides:
- Previous and next full moon and new moon dates
- Hourly fishing index forecast (with ASCII chart if using --visualize or -v)
- Top 5 best fishing hours for the specified period


Example:
```bash
python fishcast.py -l Oulu -hr 10 -sl Oulu -v 

Moon phases:
-------------
Previous full moon:      2025-01-14 00:26
Previous new moon:       2025-01-29 14:35
Next full moon:          2025-02-12 15:53
Next new moon:           2025-02-28 02:44

Fishing forecast for Oulu for next 10 hours:
---------------------------------------------
2025-02-02 02:00 - Index:  24 - Pressure: 1024.9 hPa (+0.4), Wind:  38.0° (4.5 m/s) Sealevel: 4.6 cm (+0.0)
2025-02-02 03:00 - Index:  48 - Pressure: 1025.5 hPa (+0.6), Wind:  41.0° (4.5 m/s) Sealevel: 3.6 cm (-1.0)
2025-02-02 04:00 - Index:   4 - Pressure: 1026.0 hPa (+0.5), Wind:  40.0° (4.3 m/s) Sealevel: -2.4 cm (-6.0)
2025-02-02 05:00 - Index: -10 - Pressure: 1026.0 hPa (+0.0), Wind:  33.0° (5.0 m/s) Sealevel: -6.4 cm (-4.0)
2025-02-02 06:00 - Index:   0 - Pressure: 1026.3 hPa (+0.3), Wind:  42.0° (5.1 m/s) Sealevel: -6.4 cm (+0.0)
2025-02-02 07:00 - Index:  48 - Pressure: 1026.9 hPa (+0.6), Wind:  46.0° (5.2 m/s) Sealevel: -4.4 cm (+2.0)
2025-02-02 08:00 - Index:  58 - Pressure: 1027.7 hPa (+0.8), Wind:  49.0° (5.3 m/s) Sealevel: -1.4 cm (+3.0)
2025-02-02 09:00 - Index:  48 - Pressure: 1028.3 hPa (+0.6), Wind:  51.0° (6.1 m/s) Sealevel: -3.4 cm (-2.0)
2025-02-02 10:00 - Index: -10 - Pressure: 1028.5 hPa (+0.2), Wind:  51.0° (5.9 m/s) Sealevel: -8.4 cm (-5.0)

Date/Time        │Fishing Index
─────────────────┼────────────────────────────────────────────────────────────────────────────────
Sun Feb-02 02:00 │███████████████████
Sun Feb-02 03:00 │██████████████████████████████████████
Sun Feb-02 04:00 │███
Sun Feb-02 05:00 │
Sun Feb-02 06:00 │
Sun Feb-02 07:00 │██████████████████████████████████████
Sun Feb-02 08:00 │██████████████████████████████████████████████
Sun Feb-02 09:00 │██████████████████████████████████████
Sun Feb-02 10:00 │
─────────────────┼────────────────────────────────────────────────────────────────────────────────
                 0               20              40              60              80              100
                 ┴───────────────┴───────────────┴───────────────┴───────────────┴───────────────┴

Top 5 best fishing hours in Oulu in next 10 hours:
---------------------------------------------------
2025-02-02 02:00 - Index:  24 - Pressure: 1024.9 hPa (+0.4), Wind:  38.0° (4.5 m/s) Sealevel: 4.6 cm (+0.0)
2025-02-02 03:00 - Index:  48 - Pressure: 1025.5 hPa (+0.6), Wind:  41.0° (4.5 m/s) Sealevel: 3.6 cm (-1.0)
2025-02-02 07:00 - Index:  48 - Pressure: 1026.9 hPa (+0.6), Wind:  46.0° (5.2 m/s) Sealevel: -4.4 cm (+2.0)
2025-02-02 08:00 - Index:  58 - Pressure: 1027.7 hPa (+0.8), Wind:  49.0° (5.3 m/s) Sealevel: -1.4 cm (+3.0)
2025-02-02 09:00 - Index:  48 - Pressure: 1028.3 hPa (+0.6), Wind:  51.0° (6.1 m/s) Sealevel: -3.4 cm (-2.0)
```

## License
This project is licensed under the MIT License - see below or the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Pekka Mäkinen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Data Sources
- Weather data is provided by the [Finnish Meteorological Institute](https://en.ilmatieteenlaitos.fi/open-data) under [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
- The fishing index algorithm is based on the book "Kalastuksen taito: olosuhteet, vieheet, kohteet" by Tom Berg (ISBN: 978-952-266-800-4).