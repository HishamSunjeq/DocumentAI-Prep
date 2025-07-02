# Data Preparation Tool Menu
# Interactive script to run data preparation processes

param (
    [string]$VenvPath = "$PSScriptRoot\data_prep_venv",
    [switch]$Verbose = $false  # Use -Verbose to enable detailed output
)

# Set verbose mode on by default
$Verbose = $true

# Wrap everything in a try-catch block to prevent unexpected closures
try {
    # Set color scheme
    $host.UI.RawUI.ForegroundColor = "White"
    $host.UI.RawUI.BackgroundColor = "Black"
    Clear-Host
    
    # Display verbose mode status
    if ($Verbose) {
        Write-Host "📢 Running in verbose mode - detailed output will be shown" -ForegroundColor Yellow
        Write-Host "📂 Virtual Environment: $VenvPath" -ForegroundColor Yellow
        Write-Host "📁 Working Directory: $PSScriptRoot" -ForegroundColor Yellow
        Write-Host "-----------------------------------------------------" -ForegroundColor Yellow
    }

function Show-Banner {
    Write-Host "`n==========================================" -ForegroundColor Cyan
    Write-Host "      DATA PREPARATION TOOLKIT" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Select processes to run or run all steps" -ForegroundColor Yellow
    Write-Host "------------------------------------------`n" -ForegroundColor Cyan
}

function Show-Menu {
    Show-Banner
    
    Write-Host "Available Processes:" -ForegroundColor Green
    Write-Host "1. Inspection Agent (analyze data folder)" -ForegroundColor White
    Write-Host "2. OCR Processing (extract text from documents)" -ForegroundColor White
    Write-Host "3. Text Processing and Vectorization" -ForegroundColor White
    Write-Host "4. QA Generation (create Q&A pairs)" -ForegroundColor White
    Write-Host "5. Clean JSON Files (remove metadata)" -ForegroundColor White
    Write-Host "6. Run ALL Processes (steps 1-5)" -ForegroundColor Magenta
    Write-Host "7. Check Environment Status" -ForegroundColor Yellow
    Write-Host "8. Exit" -ForegroundColor Red
    Write-Host "`n"
}

function Start-DataProcessingStep {
    param (
        [int]$processNumber
    )
    
    # Clear the console and show running message
    Clear-Host
    
    # Function to activate venv and run python command
    function Invoke-PythonInVenv {
        param (
            [string]$Command
        )
        
        Write-Host "Activating virtual environment..." -ForegroundColor Gray
        $activateScript = "$VenvPath\Scripts\Activate.ps1"
        
        # Check if the activation script exists
        if (-not (Test-Path $activateScript)) {        Write-Host "[ERROR] Virtual environment activation script not found at: $activateScript" -ForegroundColor Red
        Write-Host "Running setup script to repair..." -ForegroundColor Yellow
        Write-Host "If setup fails, see docs/setup_guide.md for manual setup instructions" -ForegroundColor Yellow
        Start-Process -FilePath "$PSScriptRoot\setup_data_prep.bat" -Wait
            
            if (-not (Test-Path $activateScript)) {
                Write-Host "[ERROR] Still cannot find virtual environment. Setup may have failed." -ForegroundColor Red
                return $false
            }
        }
        
        # Activate the virtual environment
        try {
            & $activateScript
            
            # Verify Python is working
            $pythonVersion = & python --version 2>&1
            Write-Host "   Using Python: $pythonVersion" -ForegroundColor Gray
        }
        catch {        Write-Host "[ERROR] Failed to activate virtual environment: $_" -ForegroundColor Red
        Write-Host "Please run setup_data_prep.bat to repair the environment." -ForegroundColor Yellow
        Write-Host "For troubleshooting, see docs/setup_guide.md" -ForegroundColor Yellow
            return $false
        }
        
        # Run the Python command
        Write-Host "Executing Python command..." -ForegroundColor Gray
        
        # Create a temporary file to capture the command
        $tempScriptFile = [System.IO.Path]::GetTempFileName() + ".py"
        
        # Add verbose flag to environment and ensure proper module import using absolute paths
        $verboseCommand = @"
import os
import sys

# Add the script directory to the Python path to ensure modules can be found
script_dir = '$PSScriptRoot'.replace('\\', '/')
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Enable verbose output in all modules
os.environ['VERBOSE_OUTPUT'] = 'true'
os.environ['DEBUG'] = 'true'

# Original command
$Command
"@
        
        $verboseCommand | Out-File -FilePath $tempScriptFile -Encoding utf8
        
        # Execute the Python script directly instead of via -c to see all output
        Write-Host "======================== OUTPUT START ========================" -ForegroundColor Magenta
        & python $tempScriptFile
        $result = $LASTEXITCODE
        Write-Host "========================= OUTPUT END =========================" -ForegroundColor Magenta
        
        # Clean up temp file
        Remove-Item $tempScriptFile -Force -ErrorAction SilentlyContinue
        
        Write-Host "Command completed with exit code: $result" -ForegroundColor $(if ($result -eq 0) { "Green" } else { "Red" })
        
        # Deactivate the virtual environment
        deactivate
        
        return ($result -eq 0)
    }
    
    switch ($processNumber) {
        1 {
            Write-Host "Running Step 1: Inspection Agent...`n" -ForegroundColor Cyan
            Invoke-PythonInVenv -Command "from main_verbose import step1_inspection_agent; step1_inspection_agent()"
        }
        2 {
            Write-Host "Running Step 2: OCR Processing...`n" -ForegroundColor Cyan
            Invoke-PythonInVenv -Command "from main_verbose import step2_ocr; step2_ocr()"
        }
        3 {
            Write-Host "Running Step 3: Text Processing and Vectorization...`n" -ForegroundColor Cyan
            Invoke-PythonInVenv -Command @"
import os
# Enable verbose output in all modules
os.environ['VERBOSE_OUTPUT'] = 'true'
os.environ['DEBUG'] = 'true'

from split_text_chunks import process_text_files_and_vectorize
print('Starting text processing and vectorization with detailed output...')
process_text_files_and_vectorize(verbose=True)
"@
        }
        4 {
            Write-Host "Running Step 4: QA Generation...`n" -ForegroundColor Cyan
            Invoke-PythonInVenv -Command "from main_verbose import step4_qa_generation; step4_qa_generation()"
        }
        5 {
            Write-Host "Running Step 5: Clean JSON Files...`n" -ForegroundColor Cyan
            Invoke-PythonInVenv -Command @"
import os
# Enable verbose output in all modules
os.environ['VERBOSE_OUTPUT'] = 'true'
os.environ['DEBUG'] = 'true'

from remove_metadata_fromjson import clean_json_files
print('Starting JSON cleaning with detailed output...')
clean_json_files('output/qa_pairs', 'output/cleaned_json_output', verbose=True)
"@
        }
        6 {
            Write-Host "Running ALL Steps (1-5)...`n" -ForegroundColor Magenta
            
            Write-Host "Step 1: Inspection Agent" -ForegroundColor Cyan
            $success = Invoke-PythonInVenv -Command "from main_verbose import step1_inspection_agent; step1_inspection_agent()"
            if (-not $success) { break }
            
            Write-Host "`nStep 2: OCR Processing" -ForegroundColor Cyan
            $success = Invoke-PythonInVenv -Command "from main_verbose import step2_ocr; step2_ocr()"
            if (-not $success) { break }
            
            Write-Host "`nStep 3: Text Processing and Vectorization" -ForegroundColor Cyan
            $success = Invoke-PythonInVenv -Command @"
import os
# Enable verbose output in all modules
os.environ['VERBOSE_OUTPUT'] = 'true'
os.environ['DEBUG'] = 'true'

from split_text_chunks import process_text_files_and_vectorize
print('Starting text processing and vectorization with detailed output...')
process_text_files_and_vectorize(verbose=True)
"@
            if (-not $success) { break }
            
            Write-Host "`nStep 4: QA Generation" -ForegroundColor Cyan
            $success = Invoke-PythonInVenv -Command "from main_verbose import step4_qa_generation; step4_qa_generation()"
            if (-not $success) { break }
            
            Write-Host "`nStep 5: Clean JSON Files" -ForegroundColor Cyan
            Invoke-PythonInVenv -Command @"
import os
# Enable verbose output in all modules
os.environ['VERBOSE_OUTPUT'] = 'true'
os.environ['DEBUG'] = 'true'

from remove_metadata_fromjson import clean_json_files
print('Starting JSON cleaning with detailed output...')
clean_json_files('output/qa_pairs', 'output/cleaned_json_output', verbose=True)
"@
        }
    }
    
    # Show completion message
    if ($processNumber -ne 7) {
        Write-Host "`nProcess completed! Press any key to return to menu..." -ForegroundColor Green
        $null = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

function Check-EnvironmentStatus {
    Clear-Host
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "      ENVIRONMENT STATUS CHECK" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host

    # Check virtual environment
    Write-Host "Virtual Environment:" -ForegroundColor Yellow
    if (Test-Path "$VenvPath\Scripts\Activate.ps1") {
        Write-Host "✓ Found at: $VenvPath" -ForegroundColor Green
        
        # Try activating it
        try {
            & "$VenvPath\Scripts\Activate.ps1"
            Write-Host "✓ Successfully activated" -ForegroundColor Green
            
            # Check Python version
            $pythonVersion = & python --version 2>&1
            Write-Host "✓ Python version: $pythonVersion" -ForegroundColor Green
            
            # Check installed packages
            Write-Host "`nInstalled Packages:" -ForegroundColor Yellow
            & python -m pip list
            
            # Deactivate environment
            deactivate
        }
        catch {
            Write-Host "✗ Failed to activate environment" -ForegroundColor Red
            Write-Host "  Run setup_data_prep.bat to repair" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "✗ Not found at: $VenvPath" -ForegroundColor Red
        Write-Host "  Run setup_data_prep.bat to create it" -ForegroundColor Yellow
    }
    
    # Check Ollama
    Write-Host "`nOllama Status:" -ForegroundColor Yellow
    $ollamaInstalled = $null -ne (Get-Command "ollama" -ErrorAction SilentlyContinue)
    
    if ($ollamaInstalled) {
        Write-Host "✓ Ollama is installed" -ForegroundColor Green
        
        # Check if Ollama server is running
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:11434/api/version" -TimeoutSec 2
            Write-Host "✓ Ollama server is running (version $($response.version))" -ForegroundColor Green
        }
        catch {
            Write-Host "✗ Ollama server is not running" -ForegroundColor Red
            Write-Host "  Start it with 'ollama serve' before using QA Generation" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "✗ Ollama is not installed" -ForegroundColor Red
        Write-Host "  Visit https://ollama.ai/download to install" -ForegroundColor Yellow
    }
    
    # Check GPU status
    Write-Host "`nGPU Status:" -ForegroundColor Yellow
    try {
        $gpuInfo = & nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader,nounits 2>&1
        if ($LASTEXITCODE -eq 0) {
            $gpuInfo -split "`n" | ForEach-Object {
                $gpuParts = $_ -split ", "
                if ($gpuParts.Count -ge 3) {
                    $gpuName = $gpuParts[0]
                    $usedMem = $gpuParts[1]
                    $totalMem = $gpuParts[2]
                    Write-Host "✓ $gpuName" -ForegroundColor Green
                    Write-Host "  Memory: ${usedMem}MB / ${totalMem}MB used" -ForegroundColor Green
                }
            }
        }
        else {
            Write-Host "✗ NVIDIA GPU not detected or drivers not installed" -ForegroundColor Red
            Write-Host "  For faster processing, consider using a system with GPU support" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "✗ NVIDIA GPU not detected or drivers not installed" -ForegroundColor Red
        Write-Host "  For faster processing, consider using a system with GPU support" -ForegroundColor Yellow
    }
    
    Write-Host "`nPress any key to return to menu..." -ForegroundColor Cyan
    $null = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Main loop
$choice = 0
while ($choice -ne 8) {
    Clear-Host
    Show-Menu
    
    # Get user choice
    $choice = Read-Host "Enter your choice (1-8)"
    
    # Validate input
    if ($choice -match '^\d+$' -and [int]$choice -ge 1 -and [int]$choice -le 8) {
        $choice = [int]$choice
        
        if ($choice -eq 7) {
            Check-EnvironmentStatus
        }
        elseif ($choice -ne 8) {
            Start-DataProcessingStep -processNumber $choice
        }
    }
    else {
        Write-Host "Invalid selection. Please enter a number between 1 and 8." -ForegroundColor Red
        Start-Sleep -Seconds 2
    }
}

# Exit message
Clear-Host
Write-Host "Thank you for using the Data Preparation Toolkit!" -ForegroundColor Cyan
Write-Host "Exiting..." -ForegroundColor Yellow
Start-Sleep -Seconds 1

} catch {
    # Error handling
    Write-Host "`n`nAn error occurred:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "`nPress any key to exit..." -ForegroundColor Yellow
    $null = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
