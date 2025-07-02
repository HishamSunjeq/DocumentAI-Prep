@echo on
REM Debug version of start_data_prep.bat with enhanced error reporting and detailed output
REM This version will show all commands as they execute and pause at the end

echo.
echo =============================================
echo     DATA PREPARATION TOOLKIT
echo =============================================
echo.
echo Starting Data Preparation Toolkit with detailed output...
echo For setup issues, run: setup_data_prep.bat
echo For documentation, see: docs/ folder and README.md
echo.

REM Set variables
set VENV_NAME=data_prep_venv
set VENV_PATH=%~dp0%VENV_NAME%
echo Virtual Environment Path: %VENV_PATH%

REM Check if virtual environment exists
echo Checking for virtual environment...
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at: %VENV_PATH%\Scripts\activate.bat
    echo You need to set up the environment before running the application.
    echo.
    echo Recommended action: Run setup_data_prep.bat first
    echo.
    pause
    exit /b 1
)
echo [OK] Virtual environment found.

REM Try to activate virtual environment
echo Attempting to activate virtual environment...
call "%VENV_PATH%\Scripts\activate.bat"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment with error code: %ERRORLEVEL%
    echo.
    echo Recommended action: Run setup_data_prep.bat to repair the environment
    echo.
    pause
    exit /b 1
)
echo [OK] Virtual environment activated.

REM Check if Python is working in the virtual environment
echo Checking Python in virtual environment...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not working in virtual environment with error code: %ERRORLEVEL%
    echo.
    echo Recommended action: Run setup_data_prep.bat to repair the environment
    echo.
    call "%VENV_PATH%\Scripts\deactivate.bat"
    pause
    exit /b 1
)
echo [OK] Python is working in virtual environment.

REM Set environment variables for detailed output before launching PowerShell
setlocal
set VERBOSE_OUTPUT=true
set DEBUG=true

REM Deactivate the environment before starting PowerShell
echo Deactivating virtual environment...
call "%VENV_PATH%\Scripts\deactivate.bat"

REM Check for PowerShell
echo Checking for PowerShell...
where powershell.exe
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PowerShell not found!
    echo This script requires PowerShell to be installed and available in PATH.
    echo.
    pause
    exit /b 1
)
echo [OK] PowerShell is available.

REM Check for the PowerShell script
echo Checking for PowerShell script...
if not exist "%~dp0run_data_prep.ps1" (
    echo [ERROR] PowerShell script not found at: %~dp0run_data_prep.ps1
    echo The required script is missing from the project folder.
    echo.
    pause
    exit /b 1
)
echo [OK] PowerShell script found.

REM Check PowerShell execution policy
echo Checking PowerShell execution policy...
powershell -Command "Write-Host 'Current Execution Policy:' (Get-ExecutionPolicy)" 

REM Launch PowerShell script with extensive error handling and verbose output
echo.
echo Attempting to start PowerShell script...
echo Running: powershell.exe -ExecutionPolicy Bypass -NoProfile -Command "& { try { Write-Host 'Starting run_data_prep.ps1 with detailed output...'; & '%~dp0run_data_prep.ps1' -VenvPath '%VENV_PATH%' -Verbose; if ($LASTEXITCODE -ne 0) { Write-Host 'Script exited with code:' $LASTEXITCODE -ForegroundColor Red; exit $LASTEXITCODE } } catch { Write-Host 'Error running PowerShell script:' $_.Exception.Message -ForegroundColor Red; exit 1 } }"
echo.

powershell.exe -ExecutionPolicy Bypass -NoProfile -Command "& { try { Write-Host 'Starting run_data_prep.ps1 with detailed output...'; & '%~dp0run_data_prep.ps1' -VenvPath '%VENV_PATH%' -Verbose; if ($LASTEXITCODE -ne 0) { Write-Host 'Script exited with code:' $LASTEXITCODE -ForegroundColor Red; exit $LASTEXITCODE } } catch { Write-Host 'Error running PowerShell script:' $_.Exception.Message -ForegroundColor Red; exit 1 } }"

REM Check if PowerShell ran successfully
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] PowerShell script failed with error code: %ERRORLEVEL%
    echo Please review the errors above.
    echo.
)

echo.
echo Process complete. Press any key to exit...
pause
