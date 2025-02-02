# Fishcaster
Forecaster for best fishing hours based on weather forecast and moon phases.
This script works for Finnish locations only and is not suitable for other regions.

The algorithm used in this script to calculate the fishing index is described
in the book **Kalastuksen taito: Olosuhteet, vieheet, kohteet** by **Tom Berg**. 
(ISBN: 978-952-266-800-4)

It is encouraged to buy the book to be able to interpret the results correctly.

## Description
Calculates optimal fishing times using weather forecasts from the Finnish Meteorological Institute (FMI) and moon phase data. 
Considered factors are:
- Atmospheric pressure
- Wind direction
- Moon phase
- Sea level (optional)

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
- `--sealevel`, `-sl`: Location for sealevel measurement (default: None). Use only for sea fishing.

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
                        Location for sealevel measurement (default: OFF) 
                        Possible values: Pietarsaari, Kemi, Porvoo, Vaasa,
                        Turku, Rauma, Raahe, Oulu, Mantyluoto, Kaskinen,
                        Helsinki, Hanko, Hamina, Degerby
```	


## Output
The script provides:
- Previous and next full moon and new moon dates
- Hourly fishing index and weather forecast
- Top 5 best fishing hours for the specified period (sorted by earliest time)

Example:
```bash
python fishcast.py -l Helsinki -hr 10 -v -sl Helsinki

Moon phases:

-------------
Previous full moon:      2025-01-14 00:26
Previous new moon:       2025-01-29 14:35
Next full moon:          2025-02-12 15:53
Next new moon:           2025-02-28 02:44

Fishing forecast for Helsinki for next 10 hours:
-------------------------------------------------
Sun Feb-02 19:00, I:  48, P: 1017.9 hPa (+0.7), W:   1.0° (6.2 m/s), T:  -0.5°C, S:  34.4 cm (-2.0)
Sun Feb-02 20:00, I:   0, P: 1018.1 hPa (+0.2), W:   3.0° (6.2 m/s), T:  -0.7°C, S:  34.4 cm (+0.0)
Sun Feb-02 21:00, I:   0, P: 1017.9 hPa (-0.2), W:   7.0° (6.5 m/s), T:  -0.9°C, S:  33.4 cm (-1.0)
Sun Feb-02 22:00, I:   0, P: 1017.9 hPa (+0.0), W:  13.0° (6.5 m/s), T:  -1.2°C, S:  34.4 cm (+1.0)
Sun Feb-02 23:00, I:  24, P: 1018.3 hPa (+0.4), W:  15.0° (6.0 m/s), T:  -1.4°C, S:  33.4 cm (-1.0)
Mon Feb-03 00:00, I:  24, P: 1018.8 hPa (+0.5), W:   9.0° (5.8 m/s), T:  -1.6°C, S:  33.4 cm (+0.0)
Mon Feb-03 01:00, I:  24, P: 1019.2 hPa (+0.4), W:   9.0° (5.9 m/s), T:  -1.9°C, S:  32.4 cm (-1.0)
Mon Feb-03 02:00, I:   0, P: 1019.4 hPa (+0.2), W:   9.0° (5.5 m/s), T:  -2.1°C, S:  32.4 cm (+0.0)
Mon Feb-03 03:00, I:  24, P: 1019.8 hPa (+0.4), W:  11.0° (5.0 m/s), T:  -2.4°C, S:  33.4 cm (+1.0)

Date/Time        │Fishing Index
─────────────────┼──────────────────────────────────────────────────────────────────────
Sun Feb-02 19:00 │█████████████████████████████████
Sun Feb-02 20:00 │
Sun Feb-02 21:00 │
Sun Feb-02 22:00 │
Sun Feb-02 23:00 │████████████████
Mon Feb-03 00:00 │████████████████
Mon Feb-03 01:00 │████████████████
Mon Feb-03 02:00 │
Mon Feb-03 03:00 │████████████████
─────────────────┼──────────────────────────────────────────────────────────────────────
                 0             20            40            60            80            100
                 ┴─────────────┴─────────────┴─────────────┴─────────────┴─────────────┴

Top 5 best fishing hours in Helsinki in next 10 hours:
-------------------------------------------------------
Sun Feb-02 19:00, I:  48, P: 1017.9 hPa (+0.7), W:   1.0° (6.2 m/s), T:  -0.5°C, S:  34.4 cm (-2.0)
Sun Feb-02 23:00, I:  24, P: 1018.3 hPa (+0.4), W:  15.0° (6.0 m/s), T:  -1.4°C, S:  33.4 cm (-1.0)
Mon Feb-03 00:00, I:  24, P: 1018.8 hPa (+0.5), W:   9.0° (5.8 m/s), T:  -1.6°C, S:  33.4 cm (+0.0)
Mon Feb-03 01:00, I:  24, P: 1019.2 hPa (+0.4), W:   9.0° (5.9 m/s), T:  -1.9°C, S:  32.4 cm (-1.0)
Mon Feb-03 03:00, I:  24, P: 1019.8 hPa (+0.4), W:  11.0° (5.0 m/s), T:  -2.4°C, S:  33.4 cm (+1.0)

I = Fishing index, P = Atmospheric pressure, W = Wind direction, T = Temperature, S = Sealevel
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