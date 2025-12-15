<#
=========================================================
PMCR - PowerShell launcher
=========================================================
Allows executing PMCR from a PowerShell environment:

  .\pmcr.ps1 hello

Note:
If PowerShell blocks script execution, run:
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

This script is intentionally minimal and acts only as a thin wrapper
around the Python entry point.
=========================================================
#>

python "$PSScriptRoot\pmcr.py" @args