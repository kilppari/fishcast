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

# Geoids of places supported by FMI open data API to get sea level information
GEOIDS = {
    "Pietarsaari": "-10000618",
    "Kemi": "-10017238",
    "Porvoo": "-100669",
    "Vaasa": "632978",
    "Turku": "633679",
    "Rauma": "639734",
    "Raahe": "640276",
    "Oulu": "643492",
    "Mantyluoto": "646666",  # Pori Mäntyluoto
    "Kaskinen": "653760",
    "Helsinki": "658225",
    "Hanko": "659101",
    "Hamina": "659169",
    "Degerby": "660415"  # Föglö Degerby
}

#http://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id=fmi::forecast::sealevel::point::timevaluepair&starttime=2025-02-01T23:00:00Z&endtime=2025-02-02T09:00:00Z&geoid=643492

@dataclass
class ForecastData:
    time: datetime
    pressure: float
    pressure_diff: float
    windspeed: float
    winddirection: float
    sealevel: float
    sealevel_diff: float
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

def calculate_sealevel_points(sealevel_diff: float) -> int:
    """
    Calculate points based on sea level change between consecutive measurements.
    
    Args:
        sealevel_diff: float, difference in sea level (cm) between current and previous measurement
        
    Returns:
        int: Points awarded based on sea level change:
            - +30 points: > 9 cm rise
            - +20 points: 6-9 cm rise
            - +10 points: 3-6 cm rise
            - -30 points: < -9 cm fall
            - -20 points: -6 to -9 cm fall
            - -10 points: -3 to -6 cm fall
            - 0 points: changes between -3 and +3 cm
            
    Note:
        Positive sea level changes (rising water) contribute positively to the fishing index,
        while negative changes (falling water) contribute negatively.
    """
    if sealevel_diff >= 3 and sealevel_diff <= 6:
        return 10
    elif sealevel_diff > 6 and sealevel_diff <= 9:
        return 20
    elif sealevel_diff > 9:
        return 30
    elif sealevel_diff > -6 and sealevel_diff <= -3:
        return -10
    elif sealevel_diff >= -9 and sealevel_diff <= -6:
        return -20
    elif sealevel_diff < -9:
        return -30
    return 0

def calculate_fishing_index(current_data: ForecastData, prev_data: ForecastData):
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
    points = {'pressure': 0, 'wind': 0, 'moon': 0, 'sealevel': 0}
    
    # Calculate pressure points
    pressure_diff = current_data.pressure - prev_data.pressure
    points['pressure'] = calculate_pressure_points(pressure_diff) * COEFF_PRESSURE_CHANGE
    current_data.pressure_diff = pressure_diff # Store the pressure difference

    if ARGS.sealevel != None:
        sealevel_diff = current_data.sealevel - prev_data.sealevel
        points['sealevel'] = calculate_sealevel_points(sealevel_diff)
        current_data.sealevel_diff = sealevel_diff # Store the sea level difference
    
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
            - pressure_diff: float, difference in pressure between current and previous measurement
            - windspeed: float, wind speed in m/s
            - winddirection: float, wind direction in degrees (0-360)
            - sealevel: float, sea level in cm
            - sealevel_diff: float, difference in sea level between current and previous measurement
            - fishing_index: float, fishing index

    Note:
        The FMI API provides data for Finnish locations only. The data is typically
        available in 1-hour intervals for the next 48 hours.
    """
    # Set default times if not provided
    if start_time is None:
        start_time = datetime.utcnow() - timedelta(hours=1)

    end_time = start_time + timedelta(hours=hours)
    
    # URL to get forecast data for surface measurements
    url_surface = (f"http://opendata.fmi.fi/wfs?service=WFS&version=2.0.0"
        f"&request=getFeature&storedquery_id=fmi::forecast::harmonie::surface::point::timevaluepair"
        f"&place={place}&parameters=WindDirection,WindSpeedMS,Pressure"
        f"&starttime={start_time.strftime('%Y-%m-%dT%H:%M:%S')}Z"
        f"&endtime={end_time.strftime('%Y-%m-%dT%H:%M:%S')}Z")
    
    try:
        response_surface = requests.get(url_surface)
        response_surface.raise_for_status()

        # Start parsing XML response
        root_surface = ET.fromstring(response_surface.content)

        # Find all wml2:point elements under the specific MeasurementTimeseries
        namespace = {'wml2': 'http://www.opengis.net/waterml/2.0', 'gml': 'http://www.opengis.net/gml/3.2'}
        
        def get_measurement_points(root, parameter: str) -> list:
            timeseries = root.find(f'.//wml2:MeasurementTimeseries[@gml:id="mts-1-1-{parameter}"]', namespace)
            return timeseries.findall('.//wml2:point', namespace) if timeseries else []
        
        points_pressure = get_measurement_points(root_surface, 'Pressure')
        points_windspeed = get_measurement_points(root_surface, 'WindSpeedMS')
        points_winddirection = get_measurement_points(root_surface, 'WindDirection')

        assert len(points_pressure) == len(points_windspeed) == len(points_winddirection)

        # Process pressure data and initialize forecast entries
        forecast_data = [
            {
                'time': pytz.utc.localize(datetime.strptime(point_pressure.find('.//wml2:time', namespace).text, 
                                                          '%Y-%m-%dT%H:%M:%SZ')).astimezone(pytz.timezone(timezone)),
                'pressure': float(point_pressure.find('.//wml2:value', namespace).text),
                'pressure_diff': 0.0, # To be calculated later  
                'windspeed': float(point_windspeed.find('.//wml2:value', namespace).text),
                'winddirection': float(point_winddirection.find('.//wml2:value', namespace).text),
                'sealevel': 0.0, # To be calculated later
                'sealevel_diff': 0.0, # To be calculated later
                'fishing_index': 0.0, # To be calculated later
            }
            for point_pressure, point_windspeed, point_winddirection in
              zip(points_pressure, points_windspeed, points_winddirection)
        ]

        # Get sealevel data if requested
        if ARGS.sealevel != None:
            if ARGS.sealevel not in GEOIDS:
                raise ValueError(f"Invalid sea level measurement location: {ARGS.sealevel}.\nPossible values: {', '.join(GEOIDS.keys())}")

            url_sealevel = (f"http://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature"
                f"&storedquery_id=fmi::forecast::sealevel::point::timevaluepair&"
                f"starttime={start_time.strftime('%Y-%m-%dT%H:%M:%S')}Z"
                f"&endtime={end_time.strftime('%Y-%m-%dT%H:%M:%S')}Z&geoid={GEOIDS[ARGS.sealevel]}")
            response_sealevel = requests.get(url_sealevel)
            response_sealevel.raise_for_status()
            root_sealevel = ET.fromstring(response_sealevel.content)
            points_sealevel = get_measurement_points(root_sealevel, 'SeaLevelN2000')
            assert len(points_pressure) == len(points_sealevel)

            for i, point_sealevel in enumerate(points_sealevel):
                forecast_data[i]['sealevel'] = float(point_sealevel.find('.//wml2:value', namespace).text)

        return forecast_data
        
    except requests.RequestException as e:
        print(f"Error fetching forecast data: {e}")
        return None
    except Exception as e:
        print(f"Error fetching forecast data: {e}")
        return None

def print_ascii_chart(fishing_index_forecast):
    """
    Create a simple ASCII chart showing fishing index per hour in horizontal format.
    Each row represents one hour, length represents the scaled index value.
    
    Args:
        fishing_index_forecast: List of ForecastData objects
    """
    if not fishing_index_forecast:
        return

    MAX_WIDTH = 80  # Maximum width for the bars
    
    # Get max value for scaling
    max_index = 100

    print("")
    print("Date/Time        │Fishing Index")
    print("─────────────────┼" + "─" * MAX_WIDTH)
    
    # Draw each hour's bar
    for data in fishing_index_forecast:
        # Scale the bar length to MAX_WIDTH
        bar_length = int((data.fishing_index / max_index) * MAX_WIDTH)
        time_label = data.time.strftime("%a %b-%d %H:%M")
        label = f"{time_label:16} │"
        bar = "█" * bar_length
        print(f"{label}{bar}")
    
    # Add scale at the bottom
    print("─────────────────┼" + "─" * MAX_WIDTH)
    
    # Create scale with marks at 0%, 20%, 40%, 60%, 80% and 100% of max width
    scale = "0".ljust(int(MAX_WIDTH/5))
    scale += str(int(max_index * 0.2)).ljust(int(MAX_WIDTH/5))
    scale += str(int(max_index * 0.4)).ljust(int(MAX_WIDTH/5))
    scale += str(int(max_index * 0.6)).ljust(int(MAX_WIDTH/5))
    scale += str(int(max_index * 0.8)).ljust(int(MAX_WIDTH/5))
    scale += str(int(max_index))
    print(" " * 17 + scale)

    # Add tick marks at 20% intervals
    ticks = ""
    for i in range(MAX_WIDTH + 1):
        if i == 0 or i == MAX_WIDTH // 5 or i == MAX_WIDTH * 2 // 5 or \
           i == MAX_WIDTH * 3 // 5 or i == MAX_WIDTH * 4 // 5 or i == MAX_WIDTH:
            ticks += "┴"
        else:
            ticks += "─"
    print(" " * 17 + ticks)

def forecastdata_to_str(data: ForecastData) -> str:
    str_sealevel = f"{data.sealevel:.1f} cm ({data.sealevel_diff:+.1f})" if ARGS.sealevel != None else "N/A"
    
    return (f"{data.time.strftime('%Y-%m-%d %H:%M')} - "
            f"Index: {int(data.fishing_index):>3} - "
            f"Pressure: {data.pressure:6.1f} hPa ({data.pressure_diff:+.1f}), "
            f"Wind: {data.winddirection:5.1f}° ({data.windspeed:.1f} m/s) "
            f"Sealevel: {str_sealevel}")

# Run script
if __name__ == "__main__":

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
    parser.add_argument('--visualize', '-v',
                       action='store_true',
                       help='Visualize the forecast (default: OFF)')
    parser.add_argument('--sealevel', '-sl',
                        default=None,
                        help=f'Location for sealevel measurement (default: OFF)\nPossible values: {", ".join(GEOIDS.keys())}')

    global ARGS
    ARGS = parser.parse_args()
    
    forecast_data_list = get_forecast(timezone=ARGS.timezone, 
                                    place=ARGS.location, 
                                    hours=ARGS.hours)
    fishing_index_forecast = []
    if forecast_data_list:
        text = "\nMoon phases:"
        print(text)
        print("-" * len(text))
        # Print out dates of past and future moon phases (Full moon and new moon)
        moon_phases = calculate_moon_phase_dates(datetime.now(timezone.utc))

        print(f"Previous full moon:\t {moon_phases[0].strftime('%Y-%m-%d %H:%M')}\n"
              f"Previous new moon:\t {moon_phases[2].strftime('%Y-%m-%d %H:%M')}\n"
              f"Next full moon:\t\t {moon_phases[1].strftime('%Y-%m-%d %H:%M')}\n"
              f"Next new moon:\t\t {moon_phases[3].strftime('%Y-%m-%d %H:%M')}")
    
        text = f"\nFishing forecast for {ARGS.location} for next {ARGS.hours} hours:" 
        print(text)
        print("-" * len(text))
        for i, data in enumerate(forecast_data_list):

            if i == 0:
                # Skip the first data point as it has no previous data for comparison.
                continue

            prev_data = ForecastData(**forecast_data_list[i-1])
            curr_data = ForecastData(**data)
            
            calculate_fishing_index(curr_data, prev_data)

            # Store current data into list
            fishing_index_forecast.append(curr_data)

            print(forecastdata_to_str(curr_data))

    if fishing_index_forecast:
        if ARGS.visualize:
            print_ascii_chart(fishing_index_forecast)

        # Print top 5 best fishing times
        text = f"\nTop 5 best fishing hours in {ARGS.location} in next {ARGS.hours} hours:"
        print(text)
        print("-" * len(text))
        
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
            print(forecastdata_to_str(data))
        print("")



