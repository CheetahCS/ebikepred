import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

def get_london_weather():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)


    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"

    # Define variables exactly once
    weather_vars = {
        "apparent_temperature",
        "precipitation",
        "wind_speed_10m",
        "weather_code",
        "visibility",
        "wind_gusts_10m",
        "is_day"
    }

    params = {
        "latitude": 51.5072,
        "longitude": -0.1276,
        "minutely_15": weather_vars,
        "timezone": "Europe/London",
        "past_days": 3,
        "forecast_days": 1,
    }

    responses = openmeteo.weather_api(url, params = params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    minutely_15 = response.Minutely15()

    df_weather = pd.DataFrame({
        "timestamp": pd.date_range(
            start = pd.to_datetime(minutely_15.Time(), unit = "s", utc = True),
            end =  pd.to_datetime(minutely_15.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = minutely_15.Interval()),
            inclusive = "left"
	    )
    })

    for i, var_name in enumerate(weather_vars):
        df_weather[var_name] = minutely_15.Variables(i).ValuesAsNumpy()

    return df_weather

# weather_df = get_london_weather()
# print(weather_df)
