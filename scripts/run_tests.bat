@echo off
REM Test runner script for Radar Trading Intelligence Platform

echo =====================================
echo Running Tests
echo =====================================
echo.

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo WARNING: Virtual environment is not activated
    echo Please run: venv\Scripts\activate
    echo.
    pause
    exit /b 1
)

REM Parse command line arguments
if "%1"=="unit" (
    echo Running unit tests only...
    pytest tests/unit/ -v --tb=short %2 %3 %4 %5
) else if "%1"=="integration" (
    echo Running integration tests only...
    pytest tests/integration/ -v --tb=short -m integration %2 %3 %4 %5
) else if "%1"=="functional" (
    echo Running functional tests only...
    pytest tests/functional/ -v --tb=short -m functional %2 %3 %4 %5
) else if "%1"=="coverage" (
    echo Running tests with coverage...
    pytest --cov=src --cov-report=html --cov-report=term-missing %2 %3 %4 %5
) else if "%1"=="slow" (
    echo Running tests excluding slow tests...
    pytest -v -m "not slow" %2 %3 %4 %5
) else (
    echo Running all tests...
    pytest -v --tb=short %1 %2 %3 %4 %5
)

echo.
echo Tests complete!
pause
