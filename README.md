# Fishcaster
Estimator for best fishing hours based on forecasted weather and moon phases.

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
Basic usage with default settings (Oulu, Finland):
```bash
python fishcast.py
```
Custom location and timeframe:
```bash
python fishcast.py --location Helsinki --hours 24
```
### Arguments
- `--location`, `-l`: Location in Finland (default: Oulu)
- `--hours`, `-hr`: Number of forecast hours (default: 48)
- `--timezone`, `-tz`: Timezone (default: Europe/Helsinki)

## Output
The script provides:
- Hourly fishing index forecast
- Top 5 best fishing times for the specified period