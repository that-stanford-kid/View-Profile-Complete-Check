# VANTIX

Native SwiftUI + MapKit foundation for the VANTIX Geospatial Intelligence Operating System.

## Local setup

Requirements:

- macOS
- Xcode 16+
- iOS 17+ simulator
- XcodeGen

From this folder:

```bash
brew install xcodegen
xcodegen generate
open VANTIX.xcodeproj
```

Then choose an iPhone simulator and press **Run**.

## Architecture

```text
Data Sources
    ↓
Domain Services / Adapters
    ↓
Observations
    ↓
IntelRepository
    ↓
ObjectStateResolver
    ↓
Feature ViewModels
    ↓
SwiftUI / MKMapView
```

The current project contains:

- typed multi-domain intelligence models
- mock service layer
- repository aggregation
- observation-based object state
- simulation engine
- centralized selection state
- MapKit wrapper with clustering
- custom directional annotations
- object inspector
- bottom navigation and VANTIX design system
- placeholder Intel / Graph / Alerts / More screens

All data is simulated.
