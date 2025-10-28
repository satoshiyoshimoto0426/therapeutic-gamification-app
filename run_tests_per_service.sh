#!/bin/bash
# Run pytest per service directory to avoid sys.path conflicts

set -e

echo "Running tests per service directory..."
echo "======================================"

total_tests=0
total_errors=0
failed_services=()

for service_dir in services/*/; do
    service_name=$(basename "$service_dir")
    
    # Skip __pycache__ and services without tests
    if [ "$service_name" = "__pycache__" ]; then
        continue
    fi
    
    # Check if service has test files
    if ! ls "$service_dir"test_*.py "$service_dir"*_test.py 2>/dev/null | grep -q .; then
        continue
    fi
    
    echo ""
    echo "Testing $service_name..."
    echo "------------------------"
    
    # Run pytest for this service
    if python -m pytest "$service_dir" --collect-only -q 2>&1 | tail -1 | grep -q "collected"; then
        test_count=$(python -m pytest "$service_dir" --collect-only -q 2>&1 | tail -1 | grep -oP '\d+(?= test)' || echo "0")
        echo "✓ $service_name: $test_count tests collected"
        total_tests=$((total_tests + test_count))
    else
        echo "✗ $service_name: collection failed"
        total_errors=$((total_errors + 1))
        failed_services+=("$service_name")
    fi
done

echo ""
echo "======================================"
echo "Summary:"
echo "  Total tests collected: $total_tests"
echo "  Failed services: $total_errors"

if [ ${#failed_services[@]} -gt 0 ]; then
    echo "  Services with errors:"
    for service in "${failed_services[@]}"; do
        echo "    - $service"
    done
    exit 1
else
    echo "  All services passed collection!"
    exit 0
fi
