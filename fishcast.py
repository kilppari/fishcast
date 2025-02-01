# -*- coding: utf-8 -*-
"""
This is a Python script that calculates a fishing index based on weather and moon data.

Fishing index is based on an algorithm described in the book "Kalastuksen taito: 
olosuhteet, vieheet, kohteet" by Tom Berg. (ISBN 978-952-266-800-4)

The book is only available in Finnish. The algorithm in question is meant to calculate
good fishing days in Finland. Meaning it is probably not suitable for all locations.
E.g. the effect of wind direction is likely to vary depending on location.

The script fetches forecasted weather data from the Finnish Meteorological Institute's
(FMI) open data API and moon phases through ephem library.
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import ephem, pytz
from dataclasses import dataclass
import argparse

TIMEZONE = "Europe/Helsinki"
LOCATION = "Oulu"
FORECAST_HOURS = 48 # FMI API provides forecast data between 2-3 days into future

#ARGPARSER = None

@dataclass
class ForecastData:
    time: datetime
    pressure: float
    windspeed: float
    winddirection: float
    pressure_diff: float
    fishing_index: float

def calculate_pressure_points(pressure_diff: float) -> int:
    """

    Calculate points based on pressure change between consecutive measurements.
    
    Args:
        pressure_diff: float, difference in pressure (hPa) between current and previous measurement
        
    Returns:
        int: Points awarded based on pressure change:
            - 0 points: stable pressure or unfavorable change
            - 40 points: 0.3-0.5 hPa or -2.0 to -1.0 hPa
            - 80 points: 0.5-1.0 hPa or < -2.0 hPa
            - 100 points: > 1.0 hPa
    """
    if (0.3 <= pressure_diff <= 0.5) or (-2.0 <= pressure_diff <= -1.0):
        return 40
    elif (0.5 < pressure_diff <= 1.0) or (pressure_diff < -2.0):
        return 80
    elif pressure_diff > 1.0:
        return 100
    return 0

def calculate_wind_direction_points(direction: float) -> int:
    """
    Calculate points based on wind direction.
    
    Args:
        direction: float, wind direction in degrees (0-360)
        
    Returns:
        int: Points awarded based on wind direction:
            - 100 points: South-West (202.5-247.5 degrees)
            - 80 points: South (157.5-202.5) or West (247.5-292.5)
            - 50 points: South-East (112.5-157.5) or North-West (292.5-337.5)
            - 0 points: other directions
    """
    # Constants for wind directions
    WIND_DIRECTION_POINTS = {
        'SOUTH_WEST': ((202.5, 247.5), 100),
        'SOUTH': ((157.5, 202.5), 80),
        'WEST': ((247.5, 292.5), 80),
        'SOUTH_EAST': ((112.5, 157.5), 50),
        'NORTH_WEST': ((292.5, 337.5), 50),
    }
    for (start, end), points in WIND_DIRECTION_POINTS.values():
        if start <= direction < end:
            return points
    return 0

def calculate_moon_phase_points(reference_time: datetime) -> int:
    """
    Calculate points based on proximity to full and new moon phases.
    
    Args:
        reference_time: datetime, reference point for moon calculations
        
    Returns:
        int: Points awarded based on moon phase:
            - 100 points: within 1 day of full/new moon
            - 60 points: within 2 days of full/new moon or 1 day after
            - 30 points: within 3 days of full/new moon
            - 0 points: other times
    """
    prev_full, next_full, prev_new, next_new = calculate_moon_phase_dates(reference_time)
    
    days_until_next_full = (next_full - reference_time).total_seconds() / 86400
    days_until_next_new = (next_new - reference_time).total_seconds() / 86400
    days_after_prev_full = (reference_time - prev_full).total_seconds() / 86400
    days_after_prev_new = (reference_time - prev_new).total_seconds() / 86400

    if days_until_next_full <= 1 or days_until_next_new <= 1:
        return 100
    elif days_until_next_full <= 2 or days_until_next_new <= 2 or \
         days_after_prev_full <= 1 or days_after_prev_new <= 1:
        return 60
    elif days_until_next_full <= 3 or days_until_next_new <= 3:
        return 30
    return 0

def calculate_moon_phase_dates(reference_time_utc: datetime) -> tuple[datetime, datetime, datetime, datetime]:
    """
    Get previous and next full/new moon dates relative to a reference time.
    
    Args:
        reference_time_utc: datetime, reference point for moon calculations,
        expected to be in UTC timezone

    Returns:
        tuple[datetime, datetime, datetime, datetime]: A tuple containing:
            - previous full moon datetime
            - next full moon datetime
            - previous new moon datetime
            - next new moon datetime

        All returneddatetimes are in timezone given as script argument.
    """
    # Setup observer (Use Oulu, Finland coordinates)
    observer = ephem.Observer()
    observer.lat = '65.0124'  # Oulu latitude
    observer.lon = '25.4682'  # Oulu longitude
    observer.date = reference_time_utc

    # Calculate moon phases
    prev_full = ephem.previous_full_moon(observer.date)
    next_full = ephem.next_full_moon(observer.date)
    prev_new = ephem.previous_new_moon(observer.date)
    next_new = ephem.next_new_moon(observer.date)
    
    # Convert to datetime objects to target timezone
    def localize(ephem_date):
        return pytz.utc.localize(ephem.Date(ephem_date).datetime()).astimezone(pytz.timezone(ARGS.timezone))
    
    return (
        localize(prev_full),
        localize(next_full),
        localize(prev_new),
        localize(next_new)
    )

def calculate_fishing_index(current_data: ForecastData, prev_data: ForecastData = None):
    """
    Calculate overall fishing conditions index based on weather and moon data.
    
    Args:
        current_data: ForecastData object containing current weather measurements
        prev_data: Optional ForecastData object containing previous measurements for
                   pressure difference calculation
    """
    COEFF_PRESSURE_CHANGE = 0.6
    COEFF_WIND_DIRECTION = 0.3
    COEFF_MOON_PHASE = 0.15
    points = {'pressure': 0, 'wind': 0, 'moon': 0}
    
    # Calculate pressure points
    if prev_data:
        pressure_diff = current_data.pressure - prev_data.pressure
        points['pressure'] = calculate_pressure_points(pressure_diff) * COEFF_PRESSURE_CHANGE

    current_data.pressure_diff = pressure_diff # Store the pressure difference
    
    # Calculate wind direction points
    points['wind'] = calculate_wind_direction_points(current_data.winddirection) * COEFF_WIND_DIRECTION
    points['moon'] = calculate_moon_phase_points(current_data.time.astimezone(pytz.UTC)) * COEFF_MOON_PHASE

    current_data.fishing_index = sum(points.values())


def get_forecast(
    timezone: str,
    place: str,
    hours: int,
    start_time: datetime = None
) -> list[dict] | None:

    """
    Get weather forecast data from FMI's (Finnish Meteorological Institute) open data API.
    
    Args:
        timezone: str, timezone for returned timestamps
        place: str, name of the location in Finland
        hours: int, number of hours for forecast
        start_time: datetime, start time for forecast (default: current time - 1h)

    Returns:
        list[dict] | None: List of forecast data dictionaries or None if request fails.
        Each dictionary contains:
            - time: datetime, timestamp in specified timezone
            - pressure: float, air pressure in hPa
            - windspeed: float, wind speed in m/s
            - winddirection: float, wind direction in degrees (0-360)
    
    Note:
        The FMI API provides data for Finnish locations only. The data is typically
        available in 1-hour intervals for the next 48 hours.
    """
    # Set default times if not provided
    if start_time is None:
        start_time = datetime.utcnow() - timedelta(hours=1)

    end_time = start_time + timedelta(hours=hours)
    
    url = (f"http://opendata.fmi.fi/wfs?service=WFS&version=2.0.0"
           f"&request=getFeature&storedquery_id=fmi::forecast::harmonie::surface::point::timevaluepair"
           f"&place={place}&parameters=WindDirection,WindSpeedMS,Pressure"
           f"&starttime={start_time.strftime('%Y-%m-%dT%H:%M:%S')}Z"
           f"&endtime={end_time.strftime('%Y-%m-%dT%H:%M:%S')}Z")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Start parsing XML response
        root = ET.fromstring(response.content)
        
        # Find all wml2:point elements under the specific MeasurementTimeseries
        namespace = {'wml2': 'http://www.opengis.net/waterml/2.0', 'gml': 'http://www.opengis.net/gml/3.2'}
        
        def get_measurement_points(root, parameter: str) -> list:
            timeseries = root.find(f'.//wml2:MeasurementTimeseries[@gml:id="mts-1-1-{parameter}"]', namespace)
            return timeseries.findall('.//wml2:point', namespace) if timeseries else []
        
        points_pressure = get_measurement_points(root, 'Pressure')
        points_windspeed = get_measurement_points(root, 'WindSpeedMS')
        points_winddirection = get_measurement_points(root, 'WindDirection')

        # Process pressure data and initialize forecast entries
        forecast_data = [
            {
                'time': pytz.utc.localize(datetime.strptime(point.find('.//wml2:time', namespace).text, 
                                                          '%Y-%m-%dT%H:%M:%SZ')).astimezone(pytz.timezone(timezone)),
                'pressure': float(point.find('.//wml2:value', namespace).text),
                'windspeed': 0.0,
                'winddirection': 0.0,
                'pressure_diff': 0.0,
                'fishing_index': 0.0
            }
            for point in points_pressure
        ]

        # Process wind speed data
        for i, point in enumerate(points_windspeed):
            forecast_data[i]['windspeed'] = float(point.find('.//wml2:value', namespace).text)

        # Process wind direction data
        for i, point in enumerate(points_winddirection):
            forecast_data[i]['winddirection'] = float(point.find('.//wml2:value', namespace).text)

        return forecast_data
        
    except requests.RequestException as e:
        print(f"Error fetching forecast data: {e}")
        return None

# Run script
if __name__ == "__main__":
    global ARGPARSER
    parser = argparse.ArgumentParser(description='Calculate fishing forecast based on weather and moon data.')
    parser.add_argument('--timezone', '-tz', 
                       default="Europe/Helsinki",
                       help='Timezone (default: Europe/Helsinki)')
    parser.add_argument('--location', '-l',
                       default="Oulu",
                       help='Location in Finland (default: Oulu)')
    parser.add_argument('--hours', '-hr',
                       type=int,
                       default=48,
                       help='Forecast hours (default: 48)')
    
    global ARGS
    ARGS = parser.parse_args()
    
    forecast_data_list = get_forecast(timezone=ARGS.timezone, 
                                    place=ARGS.location, 
                                    hours=ARGS.hours)
    fishing_index_forecast = []
    if forecast_data_list:
        print(f"\nFishing forecast for {ARGS.location} for next {ARGS.hours} hours:")
        print("-" * 84)
        for i, data in enumerate(forecast_data_list):
            if i == 0:
                # Skip the first data point as it has no previous data for comparison.
                continue

            prev_data = ForecastData(**forecast_data_list[i-1])
            curr_data = ForecastData(**data)
            
            calculate_fishing_index(curr_data, prev_data)

            # Store current data into list
            fishing_index_forecast.append(curr_data)

            print(f"{curr_data.time.strftime('%Y-%m-%d %H:%M')} - "
                f"Index: {int(curr_data.fishing_index):>3} - "
                f"Pressure: {curr_data.pressure:6.1f} hPa ({curr_data.pressure_diff:+.1f}), "
                f"Wind: {curr_data.winddirection:5.1f}° ({curr_data.windspeed:.1f} m/s)")

        print("\nMoon phases:")
        print("-" * 84)
        # Print out dates of past and future moon phases (Full moon and new moon)
        moon_phases = calculate_moon_phase_dates(datetime.now(timezone.utc))
        print(f"Previous full moon:\t {moon_phases[0].strftime('%Y-%m-%d %H:%M')}\n"
              f"Next full moon:\t\t {moon_phases[1].strftime('%Y-%m-%d %H:%M')}\n"
              f"Previous new moon:\t {moon_phases[2].strftime('%Y-%m-%d %H:%M')}\n"
              f"Next new moon:\t\t {moon_phases[3].strftime('%Y-%m-%d %H:%M')}")

    # Print top 5 best fishing times
    if fishing_index_forecast:
        print(f"\nTop 5 best fishing hours in {ARGS.location} in next {ARGS.hours} hours:")
        print("-" * 84)
        
        # Get top 5 by fishing index, then sort by time
        best_times = sorted(
            sorted(
                fishing_index_forecast,
                key=lambda x: x.fishing_index,
                reverse=True
            )[:5],
            key=lambda x: x.time
        )
        
        for data in best_times:
            print(
                f"{data.time.strftime('%a %b-%d %H:%M')} - "
                f"Index: {data.fishing_index:.1f} - "
                f"Pressure: {data.pressure:.1f} hPa ({data.pressure_diff:+.1f}), "
                f"Wind: {data.winddirection:.1f}° ({data.windspeed:.1f} m/s)"
            )
        print("")
