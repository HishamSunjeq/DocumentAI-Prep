# Ollama GPU Setup Script for Windows
# Run this in PowerShell as Administrator

Write-Host "🚀 Ollama GPU Setup for Windows" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ This script requires Administrator privileges" -ForegroundColor Red
    Write-Host "💡 Right-click PowerShell and 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

# Step 1: Check GPU
Write-Host "`n🔍 Checking for NVIDIA GPU..." -ForegroundColor Cyan
try {
    $gpuInfo = nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    Write-Host "✅ NVIDIA GPU detected:" -ForegroundColor Green
    Write-Host "   $gpuInfo" -ForegroundColor White
} catch {
    Write-Host "❌ NVIDIA GPU or drivers not found" -ForegroundColor Red
    Write-Host "💡 Install NVIDIA drivers from: https://www.nvidia.com/drivers" -ForegroundColor Yellow
    pause
    exit 1
}

# Step 2: Check/Install Ollama
Write-Host "`n🔍 Checking Ollama installation..." -ForegroundColor Cyan
try {
    $ollamaVersion = ollama --version
    Write-Host "✅ Ollama found: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama not found" -ForegroundColor Red
    Write-Host "💡 Installing Ollama..." -ForegroundColor Yellow
    
    # Download and install Ollama
    $ollamaUrl = "https://ollama.ai/download/windows"
    Write-Host "   Downloading from: $ollamaUrl" -ForegroundColor White
    
    # You would typically download and run the installer here
    Write-Host "   Please download and install Ollama from: $ollamaUrl" -ForegroundColor Yellow
    pause
    exit 1
}

# Step 3: Stop existing Ollama service
Write-Host "`n🛑 Stopping existing Ollama service..." -ForegroundColor Cyan
try {
    Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "✅ Ollama stopped" -ForegroundColor Green
} catch {
    Write-Host "ℹ️ No existing Ollama process found" -ForegroundColor White
}

# Step 4: Set GPU environment variables
Write-Host "`n🔧 Setting GPU environment variables..." -ForegroundColor Cyan

$envVars = @{
    "CUDA_VISIBLE_DEVICES" = "0"
    "OLLAMA_HOST" = "127.0.0.1:11434"
    "OLLAMA_NUM_PARALLEL" = "1"
    "OLLAMA_MAX_LOADED_MODELS" = "1"
    "OLLAMA_GPU_OVERHEAD" = "0"
}

foreach ($var in $envVars.GetEnumerator()) {
    [Environment]::SetEnvironmentVariable($var.Key, $var.Value, "Process")
    Set-Item -Path "env:$($var.Key)" -Value $var.Value
    Write-Host "   $($var.Key)=$($var.Value)" -ForegroundColor White
}

Write-Host "✅ Environment variables set" -ForegroundColor Green

# Step 5: Start Ollama with GPU
Write-Host "`n🚀 Starting Ollama with GPU support..." -ForegroundColor Cyan
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
Start-Sleep -Seconds 5

# Test if Ollama is running
try {
    $ollamaStatus = ollama ps
    Write-Host "✅ Ollama started successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to start Ollama" -ForegroundColor Red
    pause
    exit 1
}

# Step 6: Pull a model to test GPU
Write-Host "`n📥 Testing GPU with a small model..." -ForegroundColor Cyan
Write-Host "   Pulling tinyllama (fastest model for testing)..." -ForegroundColor White

try {
    ollama pull tinyllama
    Write-Host "✅ Model pulled successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to pull model" -ForegroundColor Red
}

# Step 7: Test GPU usage
Write-Host "`n🧪 Testing GPU usage..." -ForegroundColor Cyan
Write-Host "   Running inference test..." -ForegroundColor White

$gpuBefore = nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits
Write-Host "   GPU Memory before: $gpuBefore MB" -ForegroundColor White

# Test inference
$testPrompt = "Hello"
$testResponse = ollama run tinyllama $testPrompt --timeout 10

$gpuAfter = nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits
Write-Host "   GPU Memory after: $gpuAfter MB" -ForegroundColor White

if ([int]$gpuAfter -gt [int]$gpuBefore) {
    Write-Host "✅ GPU is being used!" -ForegroundColor Green
} else {
    Write-Host "⚠️ GPU usage not detected" -ForegroundColor Yellow
    Write-Host "💡 Try restarting your computer and running this script again" -ForegroundColor Yellow
}

# Step 8: Summary
Write-Host "`n📊 Setup Summary:" -ForegroundColor Cyan
Write-Host "   GPU Available: ✅" -ForegroundColor Green
Write-Host "   Ollama Running: ✅" -ForegroundColor Green
Write-Host "   GPU Usage: $(if ([int]$gpuAfter -gt [int]$gpuBefore) { '✅' } else { '⚠️' })" -ForegroundColor $(if ([int]$gpuAfter -gt [int]$gpuBefore) { 'Green' } else { 'Yellow' })

Write-Host "`n🎉 Setup complete!" -ForegroundColor Green
Write-Host "💡 You can now run your QA generation with GPU acceleration" -ForegroundColor Yellow
Write-Host "💡 To test: python fix_ollama_gpu.py" -ForegroundColor Yellow

pause
