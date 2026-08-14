#!/usr/bin/env bash
set -euo pipefail

if ! command -v xcodegen >/dev/null 2>&1; then
  echo "XcodeGen not found."
  echo "Install it with: brew install xcodegen"
  exit 1
fi

xcodegen generate
echo
echo "Generated VANTIX.xcodeproj"
echo "Opening Xcode..."
open VANTIX.xcodeproj
