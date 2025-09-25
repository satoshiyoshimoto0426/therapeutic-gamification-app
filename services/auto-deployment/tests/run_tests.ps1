# Auto-Deployment Integration Test Runner Script (PowerShell)
# This script provides convenient commands to run various test suites

param(
    [string]$Suite = "all",
    [string]$Config = "",
    [string]$Output = "",
    [switch]$Verbose,
    [switch]$Help
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $ScriptDir))

# Default values
$DefaultConfig = Join-Path $ScriptDir "test_config.yaml"
$DefaultOutput = Join-Path $ScriptDir "test_reports"

if (-not $Config) { $Config = $DefaultConfig }
if (-not $Output) { $Output = $DefaultOutput }

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

# Function to show usage
function Show-Usage {
    @"
Auto-Deployment Integration Test Runner (PowerShell)

Usage: .\run_tests.ps1 [OPTIONS]

Parameters:
    -Suite <string>     Test suite to run: all, integration, performance, e2e, quick, continuous, clean, status
    -Config <string>    Use custom configuration file
    -Output <string>    Output directory for reports
    -Verbose           Enable verbose output
    -Help              Show this help message

Examples:
    .\run_tests.ps1                                    # Run all tests with default config
    .\run_tests.ps1 -Suite integration                 # Run integration tests only
    .\run_tests.ps1 -Config custom.yaml -Suite performance # Run performance tests with custom config
    .\run_tests.ps1 -Verbose -Output .\reports -Suite all  # Run all tests with verbose output

Environment Variables:
    PYTHON_PATH         Path to Python executable (default: python)
    TEST_TIMEOUT        Global test timeout in seconds (default: 1800)
    SLACK_WEBHOOK_URL   Slack webhook for notifications
    SMTP_SERVER         SMTP server for email notifications
"@
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-Status "Checking prerequisites..."
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Status "Found Python: $pythonVersion"
    }
    catch {
        Write-Error "Python is required but not found in PATH"
        exit 1
    }
    
    # Check required Python packages
    try {
        python -c "import pytest, asyncio, yaml" 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Package import failed"
        }
    }
    catch {
        Write-Error "Required Python packages not found. Please install: pytest, asyncio, pyyaml"
        exit 1
    }
    
    # Check configuration file
    if (-not (Test-Path $Config)) {
        Write-Warning "Configuration file not found: $Config"
        Write-Status "Using default configuration"
    }
    
    # Create output directory
    if (-not (Test-Path $Output)) {
        New-Item -ItemType Directory -Path $Output -Force | Out-Null
    }
    
    Write-Success "Prerequisites check passed"
}

# Function to run tests
function Invoke-Tests {
    param([string]$TestSuite)
    
    $startTime = Get-Date
    
    Write-Status "Starting test execution..."
    Write-Status "Suite: $TestSuite"
    Write-Status "Config: $Config"
    Write-Status "Output: $Output"
    Write-Status "Time: $(Get-Date)"
    
    # Build command
    $runnerScript = Join-Path $ScriptDir "run_integration_tests.py"
    $cmd = "python `"$runnerScript`" --suite $TestSuite --output `"$Output`""
    
    if (Test-Path $Config) {
        $cmd += " --config `"$Config`""
    }
    
    if ($Verbose) {
        $cmd += " --verbose"
    }
    
    # Set environment variables
    $env:PYTHONPATH = "$ProjectRoot;$env:PYTHONPATH"
    
    # Run tests
    Write-Status "Executing: $cmd"
    
    try {
        Invoke-Expression $cmd
        
        if ($LASTEXITCODE -eq 0) {
            $endTime = Get-Date
            $duration = ($endTime - $startTime).TotalSeconds
            Write-Success "Tests completed successfully in $([math]::Round($duration, 2))s"
            
            # Show report location
            if (Test-Path $Output) {
                Write-Status "Reports available in: $Output"
                Get-ChildItem $Output | Select-Object -First 10 | Format-Table Name, Length, LastWriteTime
            }
            
            return $true
        }
        else {
            throw "Tests failed with exit code $LASTEXITCODE"
        }
    }
    catch {
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        Write-Error "Tests failed after $([math]::Round($duration, 2))s: $_"
        return $false
    }
}

# Function to run quick tests
function Invoke-QuickTests {
    Write-Status "Running quick test subset..."
    
    # Create temporary config for quick tests
    $quickConfig = Join-Path $Output "quick_config.yaml"
    
    $quickConfigContent = @"
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
"@
    
    $quickConfigContent | Out-File -FilePath $quickConfig -Encoding UTF8
    $script:Config = $quickConfig
    
    return Invoke-Tests "integration"
}

# Function to start continuous testing
function Start-ContinuousTesting {
    Write-Status "Starting continuous testing mode..."
    Write-Warning "Press Ctrl+C to stop continuous testing"
    
    try {
        while ($true) {
            Write-Status "Running continuous test cycle at $(Get-Date)"
            
            if (Invoke-Tests "integration") {
                Write-Success "Continuous test cycle passed"
            }
            else {
                Write-Error "Continuous test cycle failed"
            }
            
            Write-Status "Waiting 60 seconds before next cycle..."
            Start-Sleep -Seconds 60
        }
    }
    catch [System.Management.Automation.PipelineStoppedException] {
        Write-Warning "Continuous testing stopped by user"
    }
}

# Function to clean up
function Invoke-Cleanup {
    Write-Status "Cleaning up test artifacts..."
    
    # Remove test reports
    if (Test-Path $Output) {
        Remove-Item -Path $Output -Recurse -Force
        Write-Status "Removed test reports directory"
    }
    
    # Clean up any temporary files
    Get-ChildItem -Path $ScriptDir -Filter "*.tmp" -Recurse | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path $ScriptDir -Name "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    
    # Clean up Python cache
    Get-ChildItem -Path $ProjectRoot -Filter "*.pyc" -Recurse | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path $ProjectRoot -Name "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Success "Cleanup completed"
}

# Function to show test status
function Show-Status {
    Write-Status "Test Environment Status"
    Write-Host "========================"
    Write-Host "Project Root: $ProjectRoot"
    Write-Host "Script Directory: $ScriptDir"
    Write-Host "Config File: $Config"
    Write-Host "Output Directory: $Output"
    Write-Host "Python Version: $(python --version 2>&1)"
    Write-Host "Current Time: $(Get-Date)"
    
    if (Test-Path $Output) {
        Write-Host "Recent Reports:"
        Get-ChildItem $Output | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | Format-Table Name, Length, LastWriteTime
    }
    else {
        Write-Host "No reports found"
    }
}

# Main execution
function Main {
    if ($Help) {
        Show-Usage
        return
    }
    
    switch ($Suite.ToLower()) {
        { $_ -in @("all", "integration", "performance", "e2e") } {
            Test-Prerequisites
            $success = Invoke-Tests $Suite
            if (-not $success) { exit 1 }
        }
        "quick" {
            Test-Prerequisites
            $success = Invoke-QuickTests
            if (-not $success) { exit 1 }
        }
        "continuous" {
            Test-Prerequisites
            Start-ContinuousTesting
        }
        "clean" {
            Invoke-Cleanup
        }
        "status" {
            Show-Status
        }
        default {
            Write-Error "Unknown command: $Suite"
            Show-Usage
            exit 1
        }
    }
}

# Handle interrupts gracefully
trap {
    Write-Warning "Test execution interrupted"
    exit 130
}

# Run main function
Main