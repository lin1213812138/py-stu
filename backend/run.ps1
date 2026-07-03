param(
    [Parameter(Position = 0)]
    [ValidateSet("dev", "test", "lint", "typecheck", "build", "shell")]
    [string]$Command = "dev",

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ExtraArgs
)

$PYTHON = ".venv\Scripts\python"

switch ($Command) {
    "dev" {
        Write-Host "🚀 Starting dev server..." -ForegroundColor Cyan
        $port = "8000"
        if (Test-Path ".env") {
            $portLine = Get-Content ".env" | Select-String "^PORT=" | ForEach-Object { $_ -replace "^PORT=", "" }
            if ($portLine) { $port = $portLine.Trim() }
        }
        & $PYTHON -m uvicorn app.main:app --reload --port $port @ExtraArgs
    }
    "test" {
        Write-Host "🧪 Running tests..." -ForegroundColor Cyan
        & $PYTHON -m pytest @ExtraArgs
    }
    "lint" {
        Write-Host "🔍 Linting..." -ForegroundColor Cyan
        & $PYTHON -m ruff check . @ExtraArgs
    }
    "typecheck" {
        Write-Host "✅ Type checking..." -ForegroundColor Cyan
        & $PYTHON -m mypy . @ExtraArgs
    }
    "build" {
        Write-Host "📦 Building wheel..." -ForegroundColor Cyan
        & $PYTHON -m hatch build @ExtraArgs
    }
    "shell" {
        & $PYTHON @ExtraArgs
    }
}
