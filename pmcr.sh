#!/usr/bin/env sh
# =========================================================
# PMCR - Unix shell launcher
# =========================================================
# Allows executing PMCR from bash / zsh / sh environments:
#
#   ./pmcr.sh hello
#
# This script is intentionally minimal.
# Its only responsibility is to forward all arguments
# to the Python entry point.
# =========================================================

python3 "$(dirname "$0")/pmcr.py" "$@"