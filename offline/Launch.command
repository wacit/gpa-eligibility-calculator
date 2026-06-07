#!/bin/sh
# GPA & Athletic Eligibility Calculator — Portable macOS launcher
# Double-click in Finder to open the app in your default browser.
# (If macOS blocks it, right-click -> Open, or run: chmod +x Launch.command)
HERE="$(cd "$(dirname "$0")" && pwd)"
open "$HERE/app/index.html"
