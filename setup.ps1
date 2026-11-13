# setup.ps1 - menyiapkan lingkungan kerja Estimator Harga Mobil Bekas (Windows)
#
# Jalankan dari root proyek:
#   powershell -ExecutionPolicy Bypass -File .\setup.ps1

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

function Write-Step($text) { Write-Host "`n$text" -ForegroundColor Cyan }
function Write-Ok($text)   { Write-Host $text -ForegroundColor Green }
function Write-Warn($text) { Write-Host $text -ForegroundColor Yellow }
function Write-Fail($text) { Write-Host $text -ForegroundColor Red }

# 1. Cek Python
Write-Step "[1/5] Cek versi Python..."
try {
    $pyVer = (python -c "import sys; print('{}.{}'.format(*sys.version_info[:2]))").Trim()
} catch {
    Write-Fail "Python tidak ditemukan. Pasang Python 3.10 sampai 3.12 dan centang 'Add python.exe to PATH'."
    exit 1
}
if ($pyVer -notin @("3.10", "3.11", "3.12")) {
    Write-Fail "Python $pyVer tidak didukung. Pakai Python 3.10 sampai 3.12."
    exit 1
}
Write-Ok "Python $pyVer OK"

# 2. Pastikan struktur folder ada
Write-Step "[2/5] Memastikan struktur folder..."
foreach ($dir in @("backend", "frontend", "training", "models", "data", "tests")) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}
Write-Ok "Folder OK"

# 3. Buat venv jika belum ada
Write-Step "[3/5] Menyiapkan virtual environment..."
$venvPython = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Gagal membuat venv."
        exit 1
    }
    Write-Ok "venv dibuat"
} else {
    Write-Ok "venv sudah ada"
}

# 4. Instal dependensi (memakai python di dalam venv secara langsung)
Write-Step "[4/5] Menginstal dependensi..."
if (-not (Test-Path "requirements.txt")) {
    Write-Fail "requirements.txt tidak ditemukan. Jalankan 'git pull' dulu."
    exit 1
}
& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { Write-Fail "Gagal memperbarui pip."; exit 1 }

& $venvPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Fail "Instalasi dependensi gagal. Salin pesan error di atas dan kirim ke ketua tim."
    exit 1
}
Write-Ok "Dependensi terpasang"

# 5. Cek dataset (tidak ada di GitHub)
Write-Step "[5/5] Mengecek dataset..."
if (Test-Path "data\cardekho_dataset.csv") {
    Write-Ok "Dataset ditemukan."
} else {
    Write-Warn "Dataset BELUM ada. Unduh cardekho_dataset.csv dari:"
    Write-Host "https://www.kaggle.com/datasets/manishkr1754/cardekho-used-car-data"
    Write-Warn "Lalu letakkan di folder data\"
}

Write-Host ""
Write-Ok "Setup selesai."
Write-Host "Aktifkan venv setiap kali mulai kerja dengan:"
Write-Host "  .\venv\Scripts\Activate.ps1"
