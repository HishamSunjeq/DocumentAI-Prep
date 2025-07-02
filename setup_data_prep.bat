@echo off
echo.
echo =============================================
echo       DATA PREPARATION TOOLKIT SETUP
echo =============================================
echo.

REM Set variables
set VENV_NAME=data_prep_venv
set VENV_PATH=%~dp0%VENV_NAME%
set REQUIREMENTS_FILE=%~dp0requirements.txt

REM Check for Python
echo Checking for Python installation...
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and try again.
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed.
echo.





REM Check if virtual environment exists
if exist "%VENV_PATH%\Scripts\activate.bat" (
    echo Virtual environment already exists at %VENV_PATH%
    @REM echo.
    set /p UPDATE_MODE="Choose an option: (1) Just update packages, (2) Recreate environment, (3) Skip setup: "
    if "%UPDATE_MODE%"=="1" (
        echo.
        echo Updating packages in existing environment...
        goto ActivateVenv
    ) else if "%UPDATE_MODE%"=="2" (
        echo.
        echo Removing existing virtual environment...
        rmdir /s /q "%VENV_PATH%"
        goto CreateVenv
    ) else (
        echo Skipping setup...
        goto CheckOllama
    )
) else (
    :CreateVenv
    echo.
    echo Creating virtual environment at %VENV_PATH%...
    python -m venv "%VENV_PATH%"
    echo Run setup_data_prep.bat again to install dependencies.
    if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create virtual environment.
    @REM echo Please ensure you have venv module installed (pip install virtualenv)
    @REM pause
    @REM exit /b 1
)
echo [OK] Virtual environment created.
goto ActivateVenv
    echo Virtual environment not found. Creating new one...
    goto CreateVenv
)

:ActivateVenv
echo.
echo test2
echo Activating virtual environment...
echo Calling: "%VENV_PATH%\Scripts\activate.bat"

if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo [ERROR] Virtual environment activation script not found!
    echo Expected at: %VENV_PATH%\Scripts\activate.bat
    pause
    exit /b 1
)

call "%VENV_PATH%\Scripts\activate.bat"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)
echo [OK] Virtual environment activated.
echo Current Python: 
python --version
echo Current pip:
pip --version
goto InstallRequirements

:InstallRequirements
REM Check for requirements.txt
if not exist "%REQUIREMENTS_FILE%" (
    echo.
    echo [WARNING] requirements.txt not found at %REQUIREMENTS_FILE%
    echo Cannot install dependencies automatically.
    
    set /p CONTINUE="Do you want to continue anyway? (y/n): "
    if /i "%CONTINUE%"=="y" (
        goto CheckOllama
    ) else (
        echo Setup aborted.
        call "%VENV_PATH%\Scripts\deactivate.bat"
        pause
        exit /b 1
    )
)

REM Install requirements
echo.
echo Updating pip to latest version...
python -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Failed to update pip.
) else (
    echo [OK] Pip updated successfully.
)

echo.
echo Installing/updating requirements from %REQUIREMENTS_FILE%...
echo Command: pip install -U -r "%REQUIREMENTS_FILE%"
pip install -U -r "%REQUIREMENTS_FILE%"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARNING] Some packages failed to install/update.
    echo Check the error messages above.
    
    set /p CONTINUE="Do you want to continue anyway? (y/n): "
    if /i "%CONTINUE%"=="y" (
        goto CheckOllama
    ) else (
        echo Setup aborted.
        if exist "%VENV_PATH%\Scripts\deactivate.bat" (
            call "%VENV_PATH%\Scripts\deactivate.bat"
        )
        pause
        exit /b 1
    )
) else (
    echo [OK] All requirements installed/updated successfully.
)

:CheckOllama
REM Check if Ollama is installed
echo.
echo Checking for Ollama installation...
where ollama > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Ollama is not installed or not in PATH
    echo For QA Generation (Step 4), you will need Ollama installed.
    echo Visit https://ollama.ai/download to install Ollama.
) else (
    echo [OK] Ollama is installed.
    
    REM Check if Ollama server is running
    powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:11434/api/version' -TimeoutSec 2 > $null; Write-Host '[OK] Ollama server is running.' } catch { Write-Host '[WARNING] Ollama server is not running. Start it with \"ollama serve\" before using QA Generation.' }"
)

echo.
echo Checking for NVIDIA GPU and drivers...
nvidia-smi > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] NVIDIA GPU not detected or drivers not installed.
    echo       For faster processing, consider using a system with GPU support.
) else (
    echo [OK] NVIDIA GPU detected.
)

REM Create .env file if it doesn't exist
if not exist "%~dp0.env" (
    echo.
    echo Creating default .env file...
    (
        echo # Data Processing Configuration
        echo DATA_FOLDER_PATH=%~dp0data
        echo OUTPUT_FOLDER_PATH=%~dp0output
        echo OCR_OUTPUT_FOLDER_PATH=%~dp0output/ocr_output
        echo # GPU Configuration (0 for first GPU)
        echo GPU_DEVICE_ID=0
        echo GPU_AUTO_FIX=true
    ) > "%~dp0.env"
    echo [OK] Created default .env file.
)

echo.
echo =============================================
echo       SETUP COMPLETED SUCCESSFULLY
echo =============================================
echo.
echo The Data Preparation Toolkit is now ready to use!
echo Run 'start_data_prep.bat' to start the application.
echo.

REM Deactivate virtual environment
if exist "%VENV_PATH%\Scripts\deactivate.bat" (
    call "%VENV_PATH%\Scripts\deactivate.bat"
)

pause
