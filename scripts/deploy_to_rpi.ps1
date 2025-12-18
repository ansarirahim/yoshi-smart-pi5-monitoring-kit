# PowerShell Deployment Script for Raspberry Pi 5
# Target: 192.168.1.39
# User: yoshi
# Author: A.R. Ansari

$RPI_HOST = "192.168.1.39"
$RPI_USER = "yoshi"
$RPI_PASSWORD = "ansari"
$PROJECT_NAME = "raspberry-pi-smart-monitoring"
$REMOTE_DIR = "/home/yoshi/$PROJECT_NAME"
$LOCAL_DIR = Get-Location

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Deploying to Raspberry Pi 5" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Target: $RPI_USER@$RPI_HOST"
Write-Host "Remote Directory: $REMOTE_DIR"
Write-Host ""

# Check if plink/pscp are available (PuTTY tools)
$plinkPath = Get-Command plink -ErrorAction SilentlyContinue
$pscpPath = Get-Command pscp -ErrorAction SilentlyContinue

if (-not $plinkPath -or -not $pscpPath) {
    Write-Host "Error: PuTTY tools (plink/pscp) not found!" -ForegroundColor Red
    Write-Host "Please install PuTTY from: https://www.putty.org/" -ForegroundColor Yellow
    Write-Host "Or use WinSCP/FileZilla for manual transfer" -ForegroundColor Yellow
    exit 1
}

# Test SSH connection
Write-Host "Testing SSH connection..." -ForegroundColor Yellow
echo y | plink -ssh -pw $RPI_PASSWORD $RPI_USER@$RPI_HOST "echo 'Connection successful!'"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Cannot connect to $RPI_HOST" -ForegroundColor Red
    exit 1
}

# Create remote directory
Write-Host "Creating remote directory..." -ForegroundColor Yellow
plink -ssh -pw $RPI_PASSWORD $RPI_USER@$RPI_HOST "mkdir -p $REMOTE_DIR"

# Transfer files
Write-Host "Transferring files (this may take a few minutes)..." -ForegroundColor Yellow

# List of directories and files to transfer
$itemsToTransfer = @(
    "src",
    "config",
    "docs",
    "examples",
    "scripts",
    "tests",
    "systemd",
    "assets",
    "main.py",
    "requirements.txt",
    "setup.py",
    "pytest.ini",
    "VERSION",
    "README.md",
    "MILESTONES.md",
    "CODING_STANDARDS.md"
)

foreach ($item in $itemsToTransfer) {
    if (Test-Path $item) {
        Write-Host "  Transferring: $item" -ForegroundColor Gray
        pscp -r -pw $RPI_PASSWORD $item ${RPI_USER}@${RPI_HOST}:${REMOTE_DIR}/
    }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Transfer Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. SSH into RPI5: ssh $RPI_USER@$RPI_HOST" -ForegroundColor White
Write-Host "2. Navigate to project: cd $REMOTE_DIR" -ForegroundColor White
Write-Host "3. Install dependencies: pip3 install -r requirements.txt" -ForegroundColor White
Write-Host "4. Configure secrets: cp config/secrets.example.json config/secrets.json" -ForegroundColor White
Write-Host "5. Edit secrets: nano config/secrets.json" -ForegroundColor White
Write-Host "6. Edit config: nano config/config.yaml" -ForegroundColor White
Write-Host "7. Run tests: pytest tests/" -ForegroundColor White
Write-Host "8. Start application: python3 main.py" -ForegroundColor White
Write-Host ""
Write-Host "For automatic startup, run: ./scripts/install.sh" -ForegroundColor Yellow
Write-Host ""

# Offer to open SSH session
$openSSH = Read-Host "Would you like to SSH into the RPI5 now? (y/n)"
if ($openSSH -eq "y" -or $openSSH -eq "Y") {
    plink -ssh -pw $RPI_PASSWORD $RPI_USER@$RPI_HOST
}

