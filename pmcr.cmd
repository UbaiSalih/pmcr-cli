@echo off
REM =========================================================
REM PMCR - Windows CMD launcher
REM =========================================================
REM This script allows executing PMCR from cmd.exe
REM without having to type "python pmcr.py" explicitly.
REM
REM Usage:
REM   pmcr <command> [args]
REM =========================================================

REM Execute PMCR using the Python interpreter available in PATH
python "%~dp0pmcr.py" %*
