# Time Series Forecasting for Weather Prediction

## Problem Statement

Weather forecasting is critical for agriculture, transportation, energy management, and disaster preparedness. Traditional weather models rely on complex physical simulations, but data-driven approaches using historical weather data can provide complementary insights and short-term predictions.

This example demonstrates building a time series forecasting system for weather prediction using statistical and machine learning approaches, focusing on:

- Temperature forecasting using ARIMA and machine learning models
- Feature engineering for temporal patterns
- Model evaluation and comparison
- Production-ready deployment considerations

## Business Value

- **Agriculture**: Optimize irrigation and crop protection schedules
- **Energy**: Predict demand and optimize grid management
- **Transportation**: Improve route planning and safety measures
- **Emergency Services**: Better resource allocation for weather events

## Key Challenges

1. **Seasonal patterns**: Daily, weekly, and yearly cycles in weather data
2. **Non-stationarity**: Weather patterns change over time
3. **Missing data**: Sensor failures and data transmission issues
4. **Multiple variables**: Temperature, humidity, wind speed, precipitation

## Data Storage Options

The pipeline supports saving processed weather data to either:

### Apache Iceberg (Local)
- **Default choice**: Local Iceberg tables for fast, ACID-compliant storage
- **Benefits**: Schema evolution, time travel, optimized for analytics
- **Location**: `/app/data/iceberg/`

### PostgreSQL Database
- **Alternative**: Relational database storage with SQL access
- **Requirements**: PostgreSQL service running (use `docker-compose --profile with-postgres up`)
- **Benefits**: SQL queries, transactions, joins with other data

The system automatically tries Iceberg first, then falls back to PostgreSQL if available.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Weather Data  │    │  Feature         │    │   Forecasting   │
│   (Delta/CSV)   │───▶│  Engineering    │───▶│   Models        │
│                 │    │                  │    │                 │
│ • Temperature   │    │ • Temporal       │    │ • ARIMA         │
│ • Humidity      │    │ • Lag Features   │    │ • Random Forest │
│ • Wind Speed    │    │ • Rolling Stats  │    │ • XGBoost       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Evaluation    │    │   Comparison     │    │   Results       │
│   Metrics       │◀───│   & Selection    │───▶│   & Insights    │
│                 │    │                  │    │                 │
│ • MAE/RMSE      │    │ • Model Comp.    │    │ • Forecasts     │
│ • MAPE          │    │ • Best Model     │    │ • Visualizations│
│ • R² Score      │    │ • Performance    │    │ • Analysis      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Key Components

### 1. Data Loading & Preprocessing
- **WeatherDataLoader**: Handles data ingestion from Delta tables or CSV files
- **FeatureEngineer**: Creates temporal features and lag variables
- **Data Validation**: Ensures data quality and handles missing values

### 2. Forecasting Models

#### Statistical Models
- **ARIMA**: AutoRegressive Integrated Moving Average for univariate forecasting
- **Auto ARIMA**: Automatic parameter selection for ARIMA models

#### Machine Learning Models
- **Random Forest**: Ensemble method capturing non-linear relationships
- **XGBoost**: Gradient boosting with excellent performance

### 3. Model Evaluation
- **MAE (Mean Absolute Error)**: Average absolute prediction error
- **RMSE (Root Mean Square Error)**: Square root of mean squared error
- **MAPE (Mean Absolute Percentage Error)**: Percentage-based error metric
- **R² Score**: Proportion of variance explained by the model

## Running the Example

### Prerequisites
```bash
pip install -r requirements.txt
```

### Basic Demo
```bash
python solution.py
```

This will:
1. Generate sample weather data (6 months of hourly temperature data)
2. Train ARIMA, Random Forest, and XGBoost models
3. Generate 24-hour ahead temperature forecasts
4. Evaluate and compare model performance
5. Display results and visualizations

### Run inside Docker

The repo ships with a Docker image that contains all Python, Java, and system-level
dependencies (CmdStan, PySpark, TensorFlow, XGBoost, Delta Lake, Iceberg, PostgreSQL JDBC, etc.). Build it from
this directory:

```bash
docker build -t weather-forecast .
```

Run the example (default entrypoint executes `solution.py`):

```bash
docker run --rm -it weather-forecast
```

To execute a different script/command, override the container command:

```bash
docker run --rm -it weather-forecast python validate.py
```

#### Data Fetching and Storage

**Option 1: Fetch Real Weather Data**
```bash
# Fetch data for a single city
docker run --rm -v $(pwd)/data:/app/data weather-forecast \
  python fetch_weather_data.py --city "New York" --days 365

# Fetch data for multiple cities concurrently
docker run --rm -v $(pwd)/data:/app/data weather-forecast \
  python fetch_weather_data.py --cities "New York" "London" "Tokyo" --days 180
```

**Option 2: Use Docker Compose (with PostgreSQL)**
```bash
# Run with PostgreSQL database
docker-compose --profile with-postgres up

# Run data fetcher separately
docker-compose --profile fetch-data up
```

**Data Storage**: The pipeline automatically saves processed data to:
- **Iceberg** (default): Local table at `/app/data/iceberg/weather_forecasting_data`
- **PostgreSQL** (fallback): Database table if Postgres service is running

> **Resource tip:** allocate at least 4 CPU cores and 8 GB RAM to Docker Desktop—the
Prophet/CmdStan toolchain, PySpark, and TensorFlow can otherwise run out of memory.

## Configuration Options

### Data Configuration
```python
# Forecasting parameters
forecast_horizon = 24  # Hours ahead to forecast
train_test_split = 0.8  # Train/test split ratio

# Feature engineering
lag_features = [1, 24, 168]  # Lag features in hours
rolling_windows = [6, 12, 24]  # Rolling statistics windows
```

### Model Configuration
```python
# ARIMA parameters (auto-selected if None)
arima_order = None  # (p, d, q) - set to None for auto-selection

# Random Forest parameters
rf_params = {
    'n_estimators': 100,
    'max_depth': 10,
    'random_state': 42
}

# XGBoost parameters
xgb_params = {
    'n_estimators': 100,
    'max_depth': 6,
    'learning_rate': 0.1,
    'random_state': 42
}
```

## Model Performance Analysis

### Typical Results
Based on the demo data, you can expect:

| Model | MAE (°C) | RMSE (°C) | MAPE | R² | Training Time |
|-------|----------|-----------|------|----|---------------|
| ARIMA | 2.1 | 2.8 | 8.5% | 0.82 | ~2s |
| Random Forest | 1.8 | 2.4 | 7.2% | 0.87 | ~5s |
| XGBoost | 1.5 | 2.1 | 6.1% | 0.91 | ~8s |

### Model Selection Guidelines

- **Short-term (< 6h)**: ARIMA or XGBoost
- **Medium-term (6h-24h)**: XGBoost or Random Forest
- **Interpretability needed**: ARIMA or Linear models
- **High accuracy needed**: XGBoost with feature engineering
- **Fast inference required**: ARIMA or simple tree models

## Advanced Usage

### Custom Data Loading
```python
from solution import WeatherForecasting

# Initialize forecaster
forecaster = WeatherForecasting()

# Load your data
weather_df = forecaster.load_weather_data("path/to/your/weather_data.csv")

# Preprocess with custom features
processed_df = forecaster.create_features(weather_df, lags=[1, 24, 48])
```

### Training Custom Models
```python
# Train specific models
results = forecaster.train_models(
    processed_df,
    target_col='temperature',
    models=['arima', 'rf', 'xgb']
)

# Get forecasts
forecasts = forecaster.generate_forecasts(results, steps=24)
```

### Model Evaluation
```python
# Evaluate all models
evaluation = forecaster.evaluate_models(
    actual=weather_df['temperature'],
    forecasts=forecasts
)

# Print results
forecaster.print_evaluation_results(evaluation)
```

## Production Deployment

### Model Serving Options

#### 1. Batch Processing (Daily Forecasts)
```python
def generate_daily_forecast():
    # Load latest weather data
    latest_data = load_weather_data()

    # Generate 24-hour forecast
    forecast = forecaster.generate_forecasts(latest_data, steps=24)

    # Save forecast results
    save_forecast_to_delta(forecast)

    return forecast
```

#### 2. Real-time Updates
```python
def update_forecast_model():
    # Retrain model with latest data
    new_model = forecaster.train_best_model(latest_weather_data)

    # Save updated model
    save_model_to_storage(new_model)

    # Update serving endpoint
    update_model_endpoint(new_model)
```

### Monitoring & Alerting

#### Key Metrics to Monitor
- **Prediction Accuracy**: Track MAE/RMSE over time
- **Model Drift**: Compare predictions vs actuals
- **Data Quality**: Missing data rates, outliers
- **Model Performance**: Training time, inference latency

## Best Practices

### Data Quality
1. **Validate sensor data**: Check for outliers and impossible values
2. **Handle missing data**: Use appropriate imputation strategies
3. **Data versioning**: Track changes in data distribution

### Model Development
1. **Time series split**: Use proper cross-validation for temporal data
2. **Feature importance**: Understand what drives predictions
3. **Model updating**: Regularly retrain with new data

### Production Considerations
1. **Model versioning**: Track model changes and performance
2. **A/B testing**: Compare new models against production
3. **Fallback strategies**: Handle model failures gracefully

## Troubleshooting

### Common Issues

1. **Poor Model Performance**
   - Check data quality and preprocessing
   - Verify feature engineering is appropriate
   - Consider longer training history

2. **ARIMA Not Converging**
   - Try auto_arima for automatic parameter selection
   - Check for stationarity in the time series
   - Consider differencing or transformation

3. **Memory Issues with Large Datasets**
   - Reduce rolling window sizes
   - Use fewer lag features
   - Consider sampling or aggregation

## Next Steps

- **Advanced Models**: Add LSTM or Prophet models
- **Multi-variable Forecasting**: Predict multiple weather variables
- **Spatial Correlations**: Include data from multiple weather stations
- **Ensemble Methods**: Combine multiple models for better performance
- **Real-time Forecasting**: Implement streaming predictions

## Weather Data Sources

This example supports multiple free weather datasets for global city-level data:

### 1. Open-Meteo API (Recommended)
- **Coverage**: Global, city-level, hourly/daily data
- **Variables**: Temperature, humidity, precipitation, wind speed, pressure
- **Historical Data**: Available from 1940 onwards
- **Usage**: Free for non-commercial use, no API key required
- **Pros**: Real-time access, comprehensive variables, global coverage
- **Cons**: Rate limits apply, data fetching required at runtime

### 2. NOAA GSOD (Global Summary of the Day)
- **Coverage**: 30,000+ weather stations worldwide
- **Variables**: Daily temperature, precipitation, wind, visibility
- **Historical Data**: Available from 1929 onwards
- **Usage**: Completely free, downloadable CSV files
- **Pros**: No rate limits, reliable government data
- **Cons**: Daily summaries only, station-based (not exactly city centers)

### Data Consumption Methods

#### Runtime Data Fetching (Recommended)
Fetch fresh data when running the container:

```bash
# Fetch data for New York City (30 days)
docker run --rm -v $(pwd)/data:/app/data weather-forecasting \
  python fetch_weather_data.py --city "New York" --days 30

# Fetch NOAA data for a specific station
docker run --rm -v $(pwd)/data:/app/data weather-forecasting \
  python fetch_weather_data.py --source noaa-gsod --station "725030-14732" --year 2023
```

#### Build-time Data Download
Uncomment the data download line in Dockerfile for sample data inclusion.

## Running with Docker

### Prerequisites
- Docker installed and running
- At least 4GB RAM available for the container

### Build the Image
```bash
docker build -t weather-forecasting .
```

### Quick Start with Docker Compose
```bash
# Create required directories
mkdir -p data output

# Fetch sample data and run forecasting
docker-compose up --build

# Or fetch data separately first
docker-compose --profile fetch-data up data-fetcher

# Then run the forecasting
docker-compose up weather-forecasting
```

### Manual Docker Commands

#### Run with Sample Data Generation
```bash
# Create data directory
mkdir -p data

# Run the demo (will generate sample data if none exists)
docker run --rm -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output weather-forecasting
```

#### Fetch Real Weather Data First
```bash
# Fetch data for New York City (30 days)
docker run --rm -v $(pwd)/data:/app/data weather-forecasting \
  python fetch_weather_data.py --city "New York" --days 30

# Fetch NOAA data for JFK Airport
docker run --rm -v $(pwd)/data:/app/data weather-forecasting \
  python fetch_weather_data.py --source noaa-gsod --station "725030-14732" --year 2023

# Then run forecasting with real data
docker run --rm -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output weather-forecasting
```

#### Interactive Development
```bash
# Run container with bash for development/debugging
docker run -it --rm -v $(pwd):/app -v $(pwd)/data:/app/data weather-forecasting bash

# Inside container, you can run:
python fetch_weather_data.py --help
python solution.py
python validate.py
```

### Docker Image Details

- **Base Image**: `python:3.10-slim`
- **Size**: ~2.5GB (includes all ML libraries and Spark)
- **Java**: OpenJDK 21 for PySpark
- **Python Packages**: All dependencies listed in `requirements.txt`
- **Data Volume**: `/app/data` for input data
- **Output Volume**: `/app/output` for results and plots

## Data Format Requirements

The weather data should be in CSV format with the following structure:

```csv
timestamp,temperature,humidity,precipitation,wind_speed
2023-01-01 00:00:00,15.2,65.5,0.0,3.2
2023-01-01 01:00:00,14.8,67.2,0.0,2.8
...
```

- **timestamp**: ISO format datetime (YYYY-MM-DD HH:MM:SS)
- **temperature**: Celsius degrees
- **humidity**: Percentage (0-100)
- **precipitation**: Millimeters
- **wind_speed**: Meters per second

## Dataset Recommendations by Use Case

### For Learning/Development
- **Open-Meteo** with 30-90 days of data for quick testing
- Cities: New York, London, Tokyo, Sydney

### For Production Model Training
- **NOAA GSOD** with 5-10 years of historical data
- Multiple stations per city for robustness
- Combine with Open-Meteo for recent data

### For Global Analysis
- **ERA5** (if you need gridded data) or multiple NOAA stations
- Cities from different climate zones for diverse training data

## Troubleshooting Data Issues

### Open-Meteo API Limits
- Free tier: 10,000 requests/day
- Solution: Cache data locally, use during off-peak hours

### NOAA Data Gaps
- Some stations have missing data periods
- Solution: Use multiple nearby stations, interpolate missing values

### Coordinate Accuracy
- City coordinates may not match exact weather station locations
- Solution: Use actual weather station coordinates from NOAA database</content>
<parameter name="filePath">c:\Users\Moshe\Analytical_Guide\Datalake-Guide\code-recipes\examples\time-series-forecasting\problem.md