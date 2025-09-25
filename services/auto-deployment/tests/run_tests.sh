#!/bin/bash

# Auto-Deployment Integration Test Runner Script
# This script provides convenient commands to run various test suites

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Default values
CONFIG_FILE="$SCRIPT_DIR/test_config.yaml"
OUTPUT_DIR="$SCRIPT_DIR/test_reports"
VERBOSE=false
SUITE="all"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Auto-Deployment Integration Test Runner

Usage: $0 [OPTIONS] [COMMAND]

Commands:
    all                 Run all test suites (default)
    integration         Run integration tests only
    performance         Run performance tests only
    e2e                 Run end-to-end tests only
    quick               Run a quick subset of tests
    continuous          Start continuous testing mode
    clean               Clean up test reports and environments

Options:
    -c, --config FILE   Use custom configuration file
    -o, --output DIR    Output directory for reports
    -v, --verbose       Enable verbose output
    -h, --help          Show this help message

Examples:
    $0                          # Run all tests with default config
    $0 integration              # Run integration tests only
    $0 -c custom.yaml performance # Run performance tests with custom config
    $0 --verbose --output ./reports all # Run all tests with verbose output

Environment Variables:
    PYTHON_PATH         Path to Python executable (default: python3)
    TEST_TIMEOUT        Global test timeout in seconds (default: 1800)
    SLACK_WEBHOOK_URL   Slack webhook for notifications
    SMTP_SERVER         SMTP server for email notifications

EOF
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check required Python packages
    python3 -c "import pytest, asyncio, yaml" 2>/dev/null || {
        print_error "Required Python packages not found. Please install: pytest, asyncio, pyyaml"
        exit 1
    }
    
    # Check configuration file
    if [[ ! -f "$CONFIG_FILE" ]]; then
        print_warning "Configuration file not found: $CONFIG_FILE"
        print_status "Using default configuration"
    fi
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    print_success "Prerequisites check passed"
}

# Function to run tests
run_tests() {
    local suite="$1"
    local start_time=$(date +%s)
    
    print_status "Starting test execution..."
    print_status "Suite: $suite"
    print_status "Config: $CONFIG_FILE"
    print_status "Output: $OUTPUT_DIR"
    print_status "Time: $(date)"
    
    # Build command
    local cmd="python3 $SCRIPT_DIR/run_integration_tests.py"
    cmd="$cmd --suite $suite"
    cmd="$cmd --output $OUTPUT_DIR"
    
    if [[ -f "$CONFIG_FILE" ]]; then
        cmd="$cmd --config $CONFIG_FILE"
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        cmd="$cmd --verbose"
    fi
    
    # Set environment variables
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    
    # Run tests
    print_status "Executing: $cmd"
    
    if $cmd; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_success "Tests completed successfully in ${duration}s"
        
        # Show report location
        if [[ -d "$OUTPUT_DIR" ]]; then
            print_status "Reports available in: $OUTPUT_DIR"
            ls -la "$OUTPUT_DIR" | head -10
        fi
        
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_error "Tests failed after ${duration}s"
        return 1
    fi
}

# Function to run quick tests
run_quick_tests() {
    print_status "Running quick test subset..."
    
    # Create temporary config for quick tests
    local quick_config="$OUTPUT_DIR/quick_config.yaml"
    cat > "$quick_config" << EOF
test_suites:
  integration:
    enabled: true
    parallel: true
    timeout: 120
  performance:
    enabled: false
  end_to_end:
    enabled: false

test_configurations:
  - name: "basic_deployment_success"
    scenario_type: "basic_deployment"
    environment: "testing"
    should_succeed: true
    test_type: "integration"
    timeout: 30
    
  - name: "failure_recovery_test"
    scenario_type: "failure_recovery"
    environment: "testing"
    failure_count: 1
    test_type: "integration"
    timeout: 60
EOF
    
    CONFIG_FILE="$quick_config"
    run_tests "integration"
}

# Function to start continuous testing
start_continuous_testing() {
    print_status "Starting continuous testing mode..."
    print_warning "Press Ctrl+C to stop continuous testing"
    
    while true; do
        print_status "Running continuous test cycle at $(date)"
        
        if run_tests "integration"; then
            print_success "Continuous test cycle passed"
        else
            print_error "Continuous test cycle failed"
        fi
        
        print_status "Waiting 60 seconds before next cycle..."
        sleep 60
    done
}

# Function to clean up
cleanup() {
    print_status "Cleaning up test artifacts..."
    
    # Remove test reports
    if [[ -d "$OUTPUT_DIR" ]]; then
        rm -rf "$OUTPUT_DIR"
        print_status "Removed test reports directory"
    fi
    
    # Clean up any temporary files
    find "$SCRIPT_DIR" -name "*.tmp" -delete 2>/dev/null || true
    find "$SCRIPT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Clean up Python cache
    find "$PROJECT_ROOT" -name "*.pyc" -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Function to show test status
show_status() {
    print_status "Test Environment Status"
    echo "========================"
    echo "Project Root: $PROJECT_ROOT"
    echo "Script Directory: $SCRIPT_DIR"
    echo "Config File: $CONFIG_FILE"
    echo "Output Directory: $OUTPUT_DIR"
    echo "Python Version: $(python3 --version)"
    echo "Current Time: $(date)"
    
    if [[ -d "$OUTPUT_DIR" ]]; then
        echo "Recent Reports:"
        ls -lt "$OUTPUT_DIR" | head -5
    else
        echo "No reports found"
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        all|integration|performance|e2e|quick|continuous|clean|status)
            SUITE="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    case "$SUITE" in
        all|integration|performance|e2e)
            check_prerequisites
            run_tests "$SUITE"
            ;;
        quick)
            check_prerequisites
            run_quick_tests
            ;;
        continuous)
            check_prerequisites
            start_continuous_testing
            ;;
        clean)
            cleanup
            ;;
        status)
            show_status
            ;;
        *)
            print_error "Unknown command: $SUITE"
            show_usage
            exit 1
            ;;
    esac
}

# Handle interrupts gracefully
trap 'print_warning "Test execution interrupted"; exit 130' INT TERM

# Run main function
main