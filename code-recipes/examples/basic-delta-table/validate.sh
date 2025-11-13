#!/bin/bash
# Validation script for Basic Delta Table recipe
# This script verifies that the recipe works as expected

set -e  # Exit on error

echo "========================================="
echo "🧪 Validating Basic Delta Table Recipe"
echo "========================================="

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8 or later."
    exit 1
fi

echo "✅ Python found: $(python --version)"

# Check if required packages are installed
echo ""
echo "📦 Checking dependencies..."
python -c "import pyspark" 2>/dev/null || {
    echo "⚠️  PySpark not found. Installing dependencies..."
    pip install -q -r requirements.txt
}

# Run the solution
echo ""
echo "🚀 Running solution..."
python solution.py > /tmp/recipe_output.log 2>&1

# Check if the script ran successfully
if [ $? -eq 0 ]; then
    echo "✅ Solution executed successfully!"
else
    echo "❌ Solution failed to execute!"
    cat /tmp/recipe_output.log
    exit 1
fi

# Verify Delta table was created
if [ -d "/tmp/delta-tables/users/_delta_log" ]; then
    echo "✅ Delta table structure verified (_delta_log exists)"
else
    echo "❌ Delta table structure not found!"
    exit 1
fi

# Count transaction log files
log_count=$(find /tmp/delta-tables/users/_delta_log -name "*.json" | wc -l)
if [ "$log_count" -gt 0 ]; then
    echo "✅ Transaction log created ($log_count entries)"
else
    echo "❌ Transaction log not created!"
    exit 1
fi

# Display summary
echo ""
echo "========================================="
echo "✅ Validation Successful!"
echo "========================================="
echo ""
echo "📊 Summary:"
echo "   - Recipe executed without errors"
echo "   - Delta table created at /tmp/delta-tables/users"
echo "   - Transaction log verified"
echo ""
echo "🎉 This recipe is production-ready!"
