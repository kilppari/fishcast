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

## Prerequisites
- Python 3.x
- Required packages: `requests`, `ephem`, `pytz`

## Installation
```bash
pip install requests ephem pytz
```
## Usage
Basic usage to get forecast of Helsinki for next 24 hours
```bash
python fishcast.py -l Helsinki -hr 24
```

### Arguments
- `--location`, `-l`: Location in Finland (default: Oulu)
- `--hours`, `-hr`: Number of forecast hours (default: 48)
- `--timezone`, `-tz`: Timezone (default: Europe/Helsinki)
- `--visualize`, `-v`: Visualize the hourly forecast in ASCII chart (default: False)

## Output
The script provides:
- Previous and next full moon and new moon dates
- Hourly fishing index forecast (with ASCII chart if using --visualize or -v)
- Top 5 best fishing hours for the specified period

Example:
```bash
python fishcast.py -l Oulu -hr 10 -v

Moon phases:
------------------------------------------------------------------------------------
Previous full moon:      2025-01-14 00:26
Next full moon:          2025-02-12 15:53
Previous new moon:       2025-01-29 14:35
Next new moon:           2025-02-28 02:44

Fishing forecast for Oulu for next 10 hours:
------------------------------------------------------------------------------------
2025-02-01 22:00 - Index:   0 - Pressure: 1023.3 hPa (+0.3), Wind:  31.0° (4.4 m/s)
2025-02-01 23:00 - Index:   0 - Pressure: 1023.5 hPa (+0.2), Wind:  37.0° (5.3 m/s)
2025-02-02 00:00 - Index:  48 - Pressure: 1024.1 hPa (+0.6), Wind:  39.0° (4.6 m/s)
2025-02-02 01:00 - Index:  48 - Pressure: 1025.1 hPa (+1.0), Wind:  41.0° (4.0 m/s)
2025-02-02 02:00 - Index:  24 - Pressure: 1025.5 hPa (+0.4), Wind:  41.0° (4.5 m/s)
2025-02-02 03:00 - Index:  24 - Pressure: 1026.0 hPa (+0.5), Wind:  40.0° (4.3 m/s)
2025-02-02 04:00 - Index:   0 - Pressure: 1026.2 hPa (+0.2), Wind:  37.0° (4.5 m/s)
2025-02-02 05:00 - Index:   0 - Pressure: 1026.4 hPa (+0.2), Wind:  32.0° (5.0 m/s)
2025-02-02 06:00 - Index:  24 - Pressure: 1026.8 hPa (+0.4), Wind:  38.0° (5.4 m/s)

Date/Time        │ Fishing Index
─────────────────┼────────────────────────────────────────────────────────────
Sat Feb-01 22:00 │
Sat Feb-01 23:00 │
Sun Feb-02 00:00 │████████████████████████████
Sun Feb-02 01:00 │████████████████████████████
Sun Feb-02 02:00 │██████████████
Sun Feb-02 03:00 │██████████████
Sun Feb-02 04:00 │
Sun Feb-02 05:00 │
Sun Feb-02 06:00 │██████████████
─────────────────┼────────────────────────────────────────────────────────────
                 0           20          40          60          80          100
                 ┴───────────┴───────────┴───────────┴───────────┴───────────┴

Top 5 best fishing hours in Oulu in next 10 hours:
------------------------------------------------------------------------------------
Sun Feb-02 00:00 - Index: 48.0 - Pressure: 1024.1 hPa (+0.6), Wind: 39.0° (4.6 m/s)
Sun Feb-02 01:00 - Index: 48.0 - Pressure: 1025.1 hPa (+1.0), Wind: 41.0° (4.0 m/s)
Sun Feb-02 02:00 - Index: 24.0 - Pressure: 1025.5 hPa (+0.4), Wind: 41.0° (4.5 m/s)
Sun Feb-02 03:00 - Index: 24.0 - Pressure: 1026.0 hPa (+0.5), Wind: 40.0° (4.3 m/s)
Sun Feb-02 06:00 - Index: 24.0 - Pressure: 1026.8 hPa (+0.4), Wind: 38.0° (5.4 m/s)
```