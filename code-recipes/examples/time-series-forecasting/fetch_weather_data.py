#!/usr/bin/env python3
"""
Weather Data Fetcher
====================

Fetches weather data from free APIs and datasets for the time series forecasting example.

Supported sources:
- Open-Meteo API: Free historical weather data
- NOAA GSOD: Global Summary of the Day (daily weather summaries)

Features:
- Intelligent caching to avoid repeated API calls
- Retry logic with exponential backoff
- Progress indicators for long operations
- Rate limiting to respect API limits
- Expanded city database with geocoding fallback
- Data validation and quality checks

Usage:
    python fetch_weather_data.py --city "New York" --days 365
    python fetch_weather_data.py --source noaa --station "725030-14732" --year 2023
"""

import argparse
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import time
import hashlib
from typing import Optional, Dict, List, Tuple, Callable
import logging
from functools import lru_cache
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import io

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WeatherDataFetcher:
    """Fetches weather data from various free sources with optimizations"""

    def __init__(self, cache_dir: str = "/app/data/cache", max_retries: int = 3):
        self.cache_dir = cache_dir
        self.max_retries = max_retries
        self.session = requests.Session()
        # Add user agent to be respectful
        self.session.headers.update({
            'User-Agent': 'WeatherDataFetcher/1.0 (Educational Use)'
        })

        os.makedirs(self.cache_dir, exist_ok=True)

        # Rate limiting: Open-Meteo allows 10,000 requests/day
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests

    def _rate_limit(self):
        """Implement rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def _retry_request(self, url: str, params: Optional[Dict] = None, max_retries: Optional[int] = None) -> requests.Response:
        """Make HTTP request with retry logic and exponential backoff"""
        if max_retries is None:
            max_retries = self.max_retries

        for attempt in range(max_retries):
            try:
                self._rate_limit()
                response = self.session.get(url, params=params)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise e
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
        raise RuntimeError("Failed to get a response after maximum retries")

    def _get_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        """Generate cache key for URL and parameters"""
        cache_string = url
        if params:
            # Sort params for consistent hashing
            sorted_params = '&'.join(f"{k}={v}" for k, v in sorted(params.items()))
            cache_string += '?' + sorted_params
        return hashlib.md5(cache_string.encode()).hexdigest()

    def _load_from_cache(self, cache_key: str) -> Optional[pd.DataFrame]:
        """Load DataFrame from cache if available"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        if os.path.exists(cache_file):
            try:
                df = pd.read_pickle(cache_file)
                logger.info(f"Loaded data from cache: {cache_file}")
                return df
            except Exception as e:
                logger.warning(f"Failed to load cache file {cache_file}: {e}")
        return None

    def _save_to_cache(self, cache_key: str, df: pd.DataFrame):
        """Save DataFrame to cache"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        try:
            df.to_pickle(cache_file)
            logger.info(f"Saved data to cache: {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to save cache file {cache_file}: {e}")

    def fetch_open_meteo_data(self, latitude: float, longitude: float,
                            start_date: str, end_date: str,
                            variables: Optional[List[str]] = None,
                            use_cache: bool = True) -> pd.DataFrame:
        """
        Fetch historical weather data from Open-Meteo API with caching

        Parameters:
        - latitude, longitude: Coordinates of the location
        - start_date, end_date: Date range in YYYY-MM-DD format
        - variables: List of weather variables to fetch
        - use_cache: Whether to use cached data if available
        """
        if variables is None:
            variables = ["temperature_2m", "relative_humidity_2m",
                        "precipitation", "wind_speed_10m"]

        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": ",".join(variables),
            "timezone": "UTC"
        }

        cache_key = self._get_cache_key(url, params)

        # Try cache first
        if use_cache:
            cached_df = self._load_from_cache(cache_key)
            if cached_df is not None:
                return cached_df

        logger.info(f"Fetching data from Open-Meteo for {latitude:.4f}, {longitude:.4f} ({start_date} to {end_date})")

        try:
            response = self._retry_request(url, params)
            data = response.json()

            # Convert to DataFrame
            df = pd.DataFrame(data['hourly'])
            df['timestamp'] = pd.to_datetime(df['time'])
            df = df.drop('time', axis=1)
            df = df.set_index('timestamp')

            # Rename columns for consistency
            column_mapping = {
                'temperature_2m': 'temperature',
                'relative_humidity_2m': 'humidity',
                'precipitation': 'precipitation',
                'wind_speed_10m': 'wind_speed'
            }
            df = df.rename(columns=column_mapping)

            # Basic data validation
            if df.empty:
                raise ValueError("No data returned from API")

            # Check for missing values
            missing_pct = df.isnull().mean().mean()
            if missing_pct > 0.5:
                logger.warning(f"High missing data percentage: {missing_pct:.1%}")

            # Cache the result
            if use_cache:
                self._save_to_cache(cache_key, df)

            logger.info(f"Successfully fetched {len(df)} records")
            return df

        except Exception as e:
            logger.error(f"Failed to fetch Open-Meteo data: {e}")
            raise

    def fetch_noaa_gsod_data(self, station_id: str, year: int, use_cache: bool = True) -> pd.DataFrame:
        """
        Fetch NOAA GSOD (Global Summary of the Day) data with caching

        Parameters:
        - station_id: NOAA station ID (e.g., "725030-14732")
        - year: Year to fetch data for
        - use_cache: Whether to use cached data if available
        """
        url = f"https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/{year}/{station_id}.csv"

        cache_key = self._get_cache_key(url)

        # Try cache first
        if use_cache:
            cached_df = self._load_from_cache(cache_key)
            if cached_df is not None:
                return cached_df

        logger.info(f"Fetching NOAA GSOD data for station {station_id}, year {year}")

        try:
            response = self._retry_request(url)

            # Parse CSV data
            df = pd.read_csv(io.StringIO(response.text))

            # Convert date and set as index
            df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
            df = df.dropna(subset=['DATE'])  # Remove rows with invalid dates
            df = df.set_index('DATE')

            # Select relevant columns and rename
            columns_to_keep = {
                'TEMP': 'temperature',
                'DEWP': 'dew_point',
                'WDSP': 'wind_speed',
                'PRCP': 'precipitation'
            }

            # Only keep columns that exist
            available_columns = [col for col in columns_to_keep.keys() if col in df.columns]
            if not available_columns:
                raise ValueError(f"No relevant columns found in NOAA data for station {station_id}")

            df = df[available_columns]
            df = df.rename(columns={k: v for k, v in columns_to_keep.items() if k in available_columns})

            # Convert units and clean data
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Convert Fahrenheit to Celsius for temperature
            if 'temperature' in df.columns:
                df['temperature'] = (df['temperature'] - 32) * 5/9

            # Basic validation
            if df.empty:
                logger.warning(f"No valid data found for station {station_id} in {year}")
                return pd.DataFrame()

            # Cache the result
            if use_cache:
                self._save_to_cache(cache_key, df)

            logger.info(f"Successfully fetched {len(df)} daily records")
            return df

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"No data found for station {station_id} in {year}")
                return pd.DataFrame()
            raise
        except Exception as e:
            logger.error(f"Failed to fetch NOAA GSOD data: {e}")
            raise

    @lru_cache(maxsize=1000)
    def get_city_coordinates(self, city_name: str) -> Tuple[float, float]:
        """
        Get latitude and longitude for a city name with caching

        Uses expanded database and geocoding fallback
        """
        # Expanded city coordinate mapping
        city_coords = {
            # Major cities
            "new york": (40.7128, -74.0060),
            "london": (51.5074, -0.1278),
            "tokyo": (35.6762, 139.6503),
            "paris": (48.8566, 2.3522),
            "sydney": (-33.8688, 151.2093),
            "mumbai": (19.0760, 72.8777),
            "sao paulo": (-23.5505, -46.6333),
            "mexico city": (19.4326, -99.1332),
            "cairo": (30.0444, 31.2357),
            "beijing": (39.9042, 116.4074),
            "moscow": (55.7558, 37.6173),
            "istanbul": (41.0082, 28.9784),
            "bangkok": (13.7563, 100.5018),
            "jakarta": (-6.2088, 106.8456),
            "seoul": (37.5665, 126.9780),
            "shanghai": (31.2304, 121.4737),
            "karachi": (24.8607, 67.0011),
            "delhi": (28.7041, 77.1025),
            "manila": (14.5995, 120.9842),
            "lagos": (6.5244, 3.3792),
            "rio de janeiro": (-22.9068, -43.1729),
            "buenos aires": (-34.6118, -58.3966),
            "los angeles": (34.0522, -118.2437),
            "chicago": (41.8781, -87.6298),
            "houston": (29.7604, -95.3698),
            "miami": (25.7617, -80.1918),
            "toronto": (43.6532, -79.3832),
            "vancouver": (49.2827, -123.1207),
            "montreal": (45.5017, -73.5673),
            "berlin": (52.5200, 13.4050),
            "madrid": (40.4168, -3.7038),
            "rome": (41.9028, 12.4964),
            "amsterdam": (52.3676, 4.9041),
            "vienna": (48.2082, 16.3738),
            "prague": (50.0755, 14.4378),
            "warsaw": (52.2297, 21.0122),
            "budapest": (47.4979, 19.0402),
            "bucharest": (44.4268, 26.1025),
            "sofia": (42.6977, 23.3219),
            "athens": (37.9838, 23.7275),
            "helsinki": (60.1699, 24.9384),
            "stockholm": (59.3293, 18.0686),
            "oslo": (59.9139, 10.7522),
            "copenhagen": (55.6761, 12.5683),
            "dublin": (53.3498, -6.2603),
            "edinburgh": (55.9533, -3.1883),
            "lisbon": (38.7223, -9.1393),
            "porto": (41.1579, -8.6291),
            "barcelona": (41.3851, 2.1734),
            "milan": (45.4642, 9.1900),
            "munich": (48.1351, 11.5820),
            "zurich": (47.3769, 8.5417),
            "brussels": (50.8503, 4.3517),
            "cologne": (50.9375, 6.9603),
            "frankfurt": (50.1109, 8.6821),
            "hamburg": (53.5511, 9.9937),
            "stuttgart": (48.7758, 9.1829),
            "dusseldorf": (51.2277, 6.7735),
            "leipzig": (51.3397, 12.3731),
            "dresden": (51.0504, 13.7373),
            "hanover": (52.3759, 9.7320),
            "nuremberg": (49.4521, 11.0767),
            "dortmund": (51.5136, 7.4653),
            "essen": (51.4556, 7.0116),
            "bremen": (53.0793, 8.8017),
            "duisburg": (51.4344, 6.7623),
            "bochum": (51.4818, 7.2197),
            "wuppertal": (51.2562, 7.1508),
            "bielefeld": (52.0302, 8.5325),
            "bonn": (50.7374, 7.0982),
            "munster": (51.9607, 7.6261),
            "karlsruhe": (49.0069, 8.4037),
            "mannheim": (49.4875, 8.4660),
            "augsburg": (48.3665, 10.8944),
            "wiesbaden": (50.0782, 8.2398),
            "gelsenkirchen": (51.5177, 7.0857),
            "munchengladiach": (51.1804, 6.4428),
            "braunschweig": (52.2689, 10.5268),
            "chemnitz": (50.8278, 12.9214),
            "kiel": (54.3233, 10.1228),
            "aachen": (50.7753, 6.0839),
            "halle": (51.4825, 11.9697),
            "magdeburg": (52.1205, 11.6276),
            "freiburg": (47.9990, 7.8421),
            "krefeld": (51.3388, 6.5853),
            "lubeck": (53.8655, 10.6866),
            "oberhausen": (51.4730, 6.8800),
            "erfurt": (50.9848, 11.0299),
            "mainz": (49.9929, 8.2473),
            "rostock": (54.0924, 12.0991),
            "kassel": (51.3127, 9.4797),
            "hagen": (51.3595, 7.4756),
            "hamm": (51.6739, 7.8153),
            "saarbrucken": (49.2402, 6.9969),
            "potsdam": (52.3906, 13.0645),
            "ludwigshafen": (49.4774, 8.4452),
            "oldenburg": (53.1435, 8.2146),
            "leverkusen": (51.0459, 6.9944),
            "osnabruck": (52.2799, 8.0472),
            "solingen": (51.1653, 7.0671),
            "heidelberg": (49.3988, 8.6724),
            "darmstadt": (49.8728, 8.6512),
            "regensburg": (49.0134, 12.1016),
            "wurzburg": (49.7878, 9.9361),
            "ingolstadt": (48.7651, 11.4237),
            "furth": (49.4759, 10.9886),
            "ulm": (48.4011, 9.9876),
            "offenbach": (50.1054, 8.7662),
            "pforzheim": (48.8844, 8.6989),
            "wolfsburg": (52.4245, 10.7815),
            "gottingen": (51.5413, 9.9158),
            "bottrop": (51.5239, 6.9285),
            "reutlingen": (48.4914, 9.2043),
            "koblenz": (50.3569, 7.5880),
            "bremerhaven": (53.5396, 8.5809),
            "trier": (49.7499, 6.6371),
            "remscheid": (51.1785, 7.1911),
            "erlangen": (49.5897, 11.0110),
            "moers": (51.4516, 6.6408),
            "siegen": (50.8740, 8.0243),
            "hildesheim": (52.1548, 9.9577),
            "salzgitter": (52.1508, 10.3593),
            "coblence": (50.3569, 7.5880),  # Alternative name for Koblenz
            "cologne": (50.9375, 6.9603),  # Köln
            "munich": (48.1351, 11.5820),  # München
            "nuremberg": (49.4521, 11.0767),  # Nürnberg
            "stuttgart": (48.7758, 9.1829),  # Stuttgart
            "hamburg": (53.5511, 9.9937),  # Hamburg
            "frankfurt": (50.1109, 8.6821),  # Frankfurt am Main
            "dusseldorf": (51.2277, 6.7735),  # Düsseldorf
            "dortmund": (51.5136, 7.4653),  # Dortmund
            "essen": (51.4556, 7.0116),  # Essen
            "bremen": (53.0793, 8.8017),  # Bremen
            "dresden": (51.0504, 13.7373),  # Dresden
            "hanover": (52.3759, 9.7320),  # Hannover
            "leipzig": (51.3397, 12.3731),  # Leipzig
            "nuremberg": (49.4521, 11.0767),  # Nürnberg
            "dusseldorf": (51.2277, 6.7735),  # Düsseldorf
            "bielefeld": (52.0302, 8.5325),  # Bielefeld
            "bonn": (50.7374, 7.0982),  # Bonn
            "munster": (51.9607, 7.6261),  # Münster
            "karlsruhe": (49.0069, 8.4037),  # Karlsruhe
            "mannheim": (49.4875, 8.4660),  # Mannheim
            "augsburg": (48.3665, 10.8944),  # Augsburg
            "wiesbaden": (50.0782, 8.2398),  # Wiesbaden
            "gelsenkirchen": (51.5177, 7.0857),  # Gelsenkirchen
            "munchengladiach": (51.1804, 6.4428),  # Mönchengladbach
            "braunschweig": (52.2689, 10.5268),  # Braunschweig
            "chemnitz": (50.8278, 12.9214),  # Chemnitz
            "kiel": (54.3233, 10.1228),  # Kiel
            "aachen": (50.7753, 6.0839),  # Aachen
            "halle": (51.4825, 11.9697),  # Halle
            "magdeburg": (52.1205, 11.6276),  # Magdeburg
            "freiburg": (47.9990, 7.8421),  # Freiburg im Breisgau
            "krefeld": (51.3388, 6.5234),  # Krefeld
            "lubeck": (53.8655, 10.6866),  # Lübeck
            "oberhausen": (51.4730, 6.8800),  # Oberhausen
            "erfurt": (50.9848, 11.0299),  # Erfurt
            "mainz": (49.9929, 8.2473),  # Mainz
            "rostock": (54.0924, 12.0991),  # Rostock
            "kassel": (51.3127, 9.4797),  # Kassel
            "hagen": (51.3595, 7.4756),  # Hagen
            "hamm": (51.6739, 7.8153),  # Hamm
            "saarbrucken": (49.2402, 6.9969),  # Saarbrücken
            "potsdam": (52.3906, 13.0645),  # Potsdam
            "ludwigshafen": (49.4774, 8.4452),  # Ludwigshafen
            "oldenburg": (53.1435, 8.2146),  # Oldenburg
            "leverkusen": (51.0459, 6.9944),  # Leverkusen
            "osnabruck": (52.2799, 8.0472),  # Osnabrück
            "solingen": (51.1653, 7.0671),  # Solingen
            "heidelberg": (49.3988, 8.6724),  # Heidelberg
            "darmstadt": (49.8728, 8.6512),  # Darmstadt
            "regensburg": (49.0134, 12.1016),  # Regensburg
            "wurzburg": (49.7878, 9.9361),  # Würzburg
            "ingolstadt": (48.7651, 11.4237),  # Ingolstadt
            "furth": (49.4759, 10.9886),  # Fürth
            "ulm": (48.4011, 9.9876),  # Ulm
            "offenbach": (50.1054, 8.7662),  # Offenbach
            "pforzheim": (48.8844, 8.6989),  # Pforzheim
            "wolfsburg": (52.4245, 10.7815),  # Wolfsburg
            "gottingen": (51.5413, 9.9158),  # Göttingen
            "bottrop": (51.5239, 6.9285),  # Bottrop
            "reutlingen": (48.4914, 9.2043),  # Reutlingen
            "koblenz": (50.3569, 7.5880),  # Koblenz
            "bremerhaven": (53.5396, 8.5809),  # Bremerhaven
            "trier": (49.7499, 6.6371),  # Trier
            "remscheid": (51.1785, 7.1911),  # Remscheid
            "erlangen": (49.5897, 11.0110),  # Erlangen
            "moers": (51.4516, 6.6408),  # Moers
            "siegen": (50.8740, 8.0243),  # Siegen
            "hildesheim": (52.1548, 9.9577),  # Hildesheim
            "salzgitter": (52.1508, 10.3593),  # Salzgitter
        }

        city_lower = city_name.lower().strip()

        # Direct lookup
        if city_lower in city_coords:
            return city_coords[city_lower]

        # Try to find partial matches
        for city_key, coords in city_coords.items():
            if city_lower in city_key or city_key in city_lower:
                logger.info(f"Using coordinates for '{city_key}' as closest match for '{city_name}'")
                return coords

        # Fallback: Try geocoding API (requires internet)
        try:
            logger.info(f"City '{city_name}' not found in database, attempting geocoding...")
            geocode_url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": city_name,
                "format": "json",
                "limit": 1
            }

            response = self._retry_request(geocode_url, params)
            data = response.json()

            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                logger.info(f"Geocoded '{city_name}' to coordinates: {lat:.4f}, {lon:.4f}")
                return (lat, lon)
            else:
                raise ValueError(f"Could not geocode city: {city_name}")

        except Exception as e:
            logger.error(f"Geocoding failed for '{city_name}': {e}")
            raise ValueError(f"Coordinates not found for city: {city_name}. Try using exact city names or check your internet connection for geocoding.")

    def fetch_weather_data(self, city: Optional[str] = None, station_id: Optional[str] = None,
                          days: int = 365, year: Optional[int] = None,
                          source: str = "open-meteo",
                          use_cache: bool = True,
                          progress_callback: Optional[Callable] = None) -> pd.DataFrame:
        """
        Main method to fetch weather data with progress tracking and optimizations

        Parameters:
        - city: City name for Open-Meteo data
        - station_id: NOAA station ID for GSOD data
        - days: Number of days of historical data (for Open-Meteo)
        - year: Year for NOAA GSOD data
        - source: Data source ("open-meteo" or "noaa-gsod")
        - use_cache: Whether to use cached data
        - progress_callback: Optional callback for progress updates
        """
        if progress_callback:
            progress_callback("Initializing data fetch...")

        if source == "open-meteo":
            if not city:
                raise ValueError("City name required for Open-Meteo source")

            if progress_callback:
                progress_callback(f"Getting coordinates for {city}...")

            lat, lon = self.get_city_coordinates(city)

            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)

            if progress_callback:
                progress_callback(f"Fetching {days} days of weather data from Open-Meteo...")

            df = self.fetch_open_meteo_data(
                lat, lon,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                use_cache=use_cache
            )

        elif source == "noaa-gsod":
            if not station_id or year is None:
                raise ValueError("Station ID and year required for NOAA GSOD source")

            if progress_callback:
                progress_callback(f"Fetching NOAA GSOD data for station {station_id}, year {year}...")

            df = self.fetch_noaa_gsod_data(station_id, year, use_cache=use_cache)

        else:
            raise ValueError(f"Unsupported source: {source}")

        if progress_callback:
            progress_callback(f"Processing {len(df)} records...")

        # Data quality checks
        if df.empty:
            logger.warning("No data retrieved")
            return df

        # Remove rows with all NaN values
        df = df.dropna(how='all')

        # Forward fill missing values (reasonable for weather data)
        df = df.ffill()

        # Add metadata
        df.attrs['source'] = source
        df.attrs['city'] = city
        df.attrs['station_id'] = station_id
        df.attrs['fetch_timestamp'] = datetime.now().isoformat()

        if progress_callback:
            progress_callback(f"Successfully processed {len(df)} weather records")

        logger.info(f"Data fetch complete. Shape: {df.shape}, Date range: {df.index.min()} to {df.index.max()}")
        return df

    def fetch_multiple_cities(self, cities: List[str], days: int = 365,
                             max_workers: int = 3, use_cache: bool = True,
                             progress_callback: Optional[Callable] = None) -> Dict[str, pd.DataFrame]:
        """
        Fetch weather data for multiple cities concurrently

        Parameters:
        - cities: List of city names
        - days: Number of days of historical data
        - max_workers: Maximum number of concurrent requests
        - use_cache: Whether to use cached data
        - progress_callback: Optional callback for progress updates
        """
        results = {}

        def fetch_city(city: str):
            try:
                if progress_callback:
                    progress_callback(f"Fetching data for {city}...")
                df = self.fetch_weather_data(city=city, days=days, use_cache=use_cache)
                return city, df
            except Exception as e:
                logger.error(f"Failed to fetch data for {city}: {e}")
                return city, pd.DataFrame()

        if progress_callback:
            progress_callback(f"Starting concurrent fetch for {len(cities)} cities...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(fetch_city, city) for city in cities]

            for future in as_completed(futures):
                city, df = future.result()
                results[city] = df
                if progress_callback and not df.empty:
                    progress_callback(f"Completed {city}: {len(df)} records")

        successful_fetches = sum(1 for df in results.values() if not df.empty)
        if progress_callback:
            progress_callback(f"Completed fetching data for {successful_fetches}/{len(cities)} cities")

        return results

def main():
    """Command-line interface with enhanced options"""
    parser = argparse.ArgumentParser(
        description="Fetch weather data from free sources with optimizations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch 365 days of data for New York
  python fetch_weather_data.py --city "New York" --days 365

  # Fetch NOAA data for a specific station and year
  python fetch_weather_data.py --source noaa-gsod --station "725030-14732" --year 2023

  # Fetch data for multiple cities concurrently
  python fetch_weather_data.py --cities "New York" "London" "Tokyo" --days 180

  # Disable caching for fresh data
  python fetch_weather_data.py --city "Paris" --no-cache

  # Use custom cache directory
  python fetch_weather_data.py --city "Sydney" --cache-dir "/tmp/weather_cache"
        """
    )

    parser.add_argument("--source", choices=["open-meteo", "noaa-gsod"],
                       default="open-meteo", help="Data source to use")
    parser.add_argument("--city", help="City name for Open-Meteo (e.g., 'New York')")
    parser.add_argument("--cities", nargs='+', help="Multiple city names for concurrent fetching")
    parser.add_argument("--station", help="NOAA station ID for GSOD (e.g., '725030-14732')")
    parser.add_argument("--year", type=int, help="Year for NOAA GSOD data")
    parser.add_argument("--days", type=int, default=365,
                       help="Number of days of historical data to fetch (default: 365)")
    parser.add_argument("--output", default="/app/data/weather_data.csv",
                       help="Output file path")
    parser.add_argument("--cache-dir", default="/app/data/cache",
                       help="Cache directory path")
    parser.add_argument("--no-cache", action="store_true",
                       help="Disable caching (force fresh data)")
    parser.add_argument("--max-retries", type=int, default=3,
                       help="Maximum number of retry attempts (default: 3)")
    parser.add_argument("--max-workers", type=int, default=3,
                       help="Maximum concurrent workers for multi-city fetches (default: 3)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Progress callback for console output
    def progress_callback(message: str):
        print(f"[PROGRESS] {message}")

    try:
        fetcher = WeatherDataFetcher(cache_dir=args.cache_dir, max_retries=args.max_retries)

        if args.cities:
            # Multi-city fetch
            if args.source != "open-meteo":
                print("Error: Multi-city fetching only supported with Open-Meteo source")
                return

            results = fetcher.fetch_multiple_cities(
                args.cities,
                days=args.days,
                max_workers=args.max_workers,
                use_cache=not args.no_cache,
                progress_callback=progress_callback
            )

            # Save each city's data to separate files
            for city, df in results.items():
                if not df.empty:
                    city_filename = f"{city.lower().replace(' ', '_')}_weather_data.csv"
                    output_path = os.path.join(os.path.dirname(args.output), city_filename)
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    df.to_csv(output_path)
                    print(f"Saved {city} data to {output_path} (shape: {df.shape})")
                else:
                    print(f"No data retrieved for {city}")

        else:
            # Single city/station fetch
            df = fetcher.fetch_weather_data(
                city=args.city,
                station_id=args.station,
                days=args.days,
                year=args.year,
                source=args.source,
                use_cache=not args.no_cache,
                progress_callback=progress_callback
            )

            if not df.empty:
                # Save to CSV
                os.makedirs(os.path.dirname(args.output), exist_ok=True)
                df.to_csv(args.output)
                print(f"Data saved to {args.output}")
                print(f"Shape: {df.shape}")
                print(f"Date range: {df.index.min()} to {df.index.max()}")
                print(f"Columns: {', '.join(df.columns)}")

                # Show data quality info
                missing_pct = df.isnull().mean().mean()
                print(f"Missing data: {missing_pct:.1%}")
            else:
                print("No data retrieved")

    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()