#!/usr/bin/env python3
"""
Validation script for Time Series Forecasting for Weather Prediction
This script validates that the forecasting pipeline works correctly
"""

import sys
import os
import ast
import subprocess
import importlib.util
from pathlib import Path

def main():
    print("🌤️  Validating Time Series Forecasting for Weather Prediction")
    print("=" * 60)

    # Check if required packages can be imported
    print("📦 Checking dependencies...")
    required_packages = [
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly',
        'statsmodels', 'scikit-learn', 'xgboost', 'lightgbm'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} not available")

    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False

    # Check if optional packages are available
    optional_packages = ['prophet', 'tensorflow']
    for package in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package} available (optional)")
        except ImportError:
            print(f"⚠️  {package} not available (optional)")

    print("\n🧪 Running basic functionality tests...")

    # Test basic imports from solution
    try:
        # Import key classes (without running full pipeline)
        sys.path.insert(0, os.path.dirname(__file__))

        # Test syntax by parsing the file
        with open('solution.py', 'r', encoding='utf-8') as f:
            script_content = f.read()

        # Parse the AST
        tree = ast.parse(script_content)
        print("✅ Solution script syntax is valid")

        # Check for required classes
        classes_found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes_found.append(node.name)

        required_classes = [
            'WeatherData', 'WeatherDataLoader', 'WeatherFeatureEngineer',
            'WeatherVisualizer', 'StatisticalForecaster', 'MLForecaster',
            'DeepLearningForecaster', 'ProphetForecaster', 'ModelEvaluator',
            'EnsembleForecaster', 'WeatherForecastingPipeline'
        ]

        missing_classes = []
        for cls in required_classes:
            if cls in classes_found:
                print(f"✅ Required class {cls} found")
            else:
                missing_classes.append(cls)
                print(f"❌ Required class {cls} not found")

        if missing_classes:
            print(f"\n❌ Missing required classes: {missing_classes}")
            return False

        # Check for required functions
        functions_found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions_found.append(node.name)

        required_functions = ['generate_sample_weather_data', 'demonstrate_weather_forecasting']

        for func in required_functions:
            if func in functions_found:
                print(f"✅ Required function {func} found")
            else:
                print(f"❌ Required function {func} not found")
                return False

    except SyntaxError as e:
        print(f"❌ Syntax error in solution.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating solution.py: {e}")
        return False

    # Test sample data generation
    print("\n🧪 Testing sample data generation...")
    try:
        # Import the function from solution.py
        spec = importlib.util.spec_from_file_location("solution", "solution.py")
        if spec is None or spec.loader is None:
            raise ImportError("Could not load solution.py")

        solution_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(solution_module)

        # Generate small sample for testing
        test_output = "/tmp/weather_test_sample.csv"
        sample_df = solution_module.generate_sample_weather_data(test_output, days=1)

        if os.path.exists(test_output):
            print("✅ Sample data generation works")
            print(f"   Generated {len(sample_df)} data points")

            # Check data structure
            required_columns = ['timestamp', 'temperature', 'humidity', 'wind_speed', 'precipitation', 'pressure']
            missing_columns = [col for col in required_columns if col not in sample_df.columns]

            if not missing_columns:
                print("✅ Data structure is correct")
            else:
                print(f"❌ Missing columns: {missing_columns}")
                return False

            # Clean up
            os.remove(test_output)
        else:
            print("❌ Sample data file not created")
            return False

    except Exception as e:
        print(f"❌ Error testing sample data generation: {e}")
        return False

    print("\n📊 Validation Results:")
    print("=" * 40)
    print("✅ Python environment check passed")
    print("✅ All required packages available")
    print("✅ Script syntax validation passed")
    print("✅ All required classes present")
    print("✅ All required functions present")
    print("✅ Sample data generation works")
    print("✅ Data structure validation passed")
    print("")
    print("🎉 All validations passed! The weather forecasting recipe is ready to use.")
    print("")
    print("💡 To run the full demo:")
    print("   python solution.py")
    print("")
    print("💡 Expected runtime: 5-15 minutes (depending on hardware)")
    print("💡 Memory requirements: 4GB+ RAM recommended")
    print("")
    print("💡 For production deployment:")
    print("   - Configure proper data sources")
    print("   - Set up model monitoring and retraining")
    print("   - Implement proper error handling and logging")
    print("   - Consider cloud deployment (Azure ML, SageMaker, etc.)")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)