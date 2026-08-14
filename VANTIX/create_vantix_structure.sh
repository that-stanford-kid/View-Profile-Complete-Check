#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-VANTIX}"
mkdir -p "$ROOT"

mkdir -p "$ROOT/."
cat > "$ROOT/FILE_TREE.txt" <<'__VANTIX_FILE_6996284952018526233__'
VANTIX/
    README.md
    VANTIX/
        App/
            AppEnvironment.swift
            ContentView.swift
            VANTIXApp.swift
        Core/
            DesignSystem/
                VantixColors.swift
                VantixMetrics.swift
            Extensions/
                Color+Intel.swift
        Data/
            MockServices/
                MockAircraftService.swift
                MockEventService.swift
                MockFacilityService.swift
                MockFactory.swift
                MockSatelliteService.swift
                MockVesselService.swift
            Repositories/
                IntelRepository.swift
            Simulation/
                SimulationEngine.swift
        Domain/
            Models/
                Enums.swift
                IntelDomain.swift
                IntelObject.swift
                ObjectState.swift
                Observation.swift
                SelectionState.swift
                SourceRecord.swift
            Protocols/
                IntelDomainService.swift
                IntelRepositoryProtocol.swift
        Features/
            Alerts/
                Views/
                    AlertsPlaceholderView.swift
            Graph/
                Views/
                    GraphPlaceholderView.swift
            Intel/
                Views/
                    IntelPlaceholderView.swift
            Map/
                Components/
                    BottomNavigation.swift
                    FloatingMapControls.swift
                    MapPlaceholderPanel.swift
                    TopStatusBar.swift
                MapKit/
                    IntelAnnotation.swift
                    IntelAnnotationView.swift
                    VantixMapView.swift
                ViewModels/
                    MapViewModel.swift
                Views/
                    MainMapView.swift
                    ObjectInspectorView.swift
            More/
                Views/
                    MorePlaceholderView.swift
        Resources/
            Assets.xcassets/
                AppIcon.appiconset/
                    Contents.json
                Contents.json
            Info.plist
    project.yml
    setup.sh
__VANTIX_FILE_6996284952018526233__

mkdir -p "$ROOT/."
cat > "$ROOT/README.md" <<'__VANTIX_FILE_5433156974851226631__'
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
__VANTIX_FILE_5433156974851226631__

mkdir -p "$ROOT/VANTIX/App"
cat > "$ROOT/VANTIX/App/AppEnvironment.swift" <<'__VANTIX_FILE_1468761709388254368__'
import Foundation

@MainActor
final class AppEnvironment: ObservableObject {
    let repository: IntelRepository
    let simulationEngine: SimulationEngine

    @Published var selection = SelectionState()
    @Published var selectedTab: AppTab = .map

    init() {
        let services: [any IntelDomainService] = [
            MockAircraftService(),
            MockVesselService(),
            MockSatelliteService(),
            MockFacilityService(),
            MockEventService()
        ]

        let repository = IntelRepository(services: services)
        self.repository = repository
        self.simulationEngine = SimulationEngine(repository: repository)
    }

    func bootstrap() async {
        guard repository.objectCount == 0 else { return }
        await repository.load()
        simulationEngine.start()
    }
}

enum AppTab: String, CaseIterable, Identifiable {
    case map = "MAP"
    case intel = "INTEL"
    case graph = "GRAPH"
    case alerts = "ALERTS"
    case more = "MORE"

    var id: String { rawValue }

    var icon: String {
        switch self {
        case .map: "map.fill"
        case .intel: "waveform.path.ecg.rectangle"
        case .graph: "point.3.connected.trianglepath.dotted"
        case .alerts: "bell.fill"
        case .more: "ellipsis"
        }
    }
}
__VANTIX_FILE_1468761709388254368__

mkdir -p "$ROOT/VANTIX/App"
cat > "$ROOT/VANTIX/App/ContentView.swift" <<'__VANTIX_FILE_8048975684080075013__'
import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var environment: AppEnvironment

    var body: some View {
        ZStack(alignment: .bottom) {
            Group {
                switch environment.selectedTab {
                case .map:
                    MainMapView()
                case .intel:
                    IntelPlaceholderView()
                case .graph:
                    GraphPlaceholderView()
                case .alerts:
                    AlertsPlaceholderView()
                case .more:
                    MorePlaceholderView()
                }
            }

            BottomNavigation(selectedTab: $environment.selectedTab)
        }
        .ignoresSafeArea(edges: .bottom)
        .task {
            await environment.bootstrap()
        }
    }
}
__VANTIX_FILE_8048975684080075013__

mkdir -p "$ROOT/VANTIX/App"
cat > "$ROOT/VANTIX/App/VANTIXApp.swift" <<'__VANTIX_FILE_346778858172810074__'
import SwiftUI

@main
struct VANTIXApp: App {
    @StateObject private var environment = AppEnvironment()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(environment)
                .preferredColorScheme(.dark)
        }
    }
}
__VANTIX_FILE_346778858172810074__

mkdir -p "$ROOT/VANTIX/Core/DesignSystem"
cat > "$ROOT/VANTIX/Core/DesignSystem/VantixColors.swift" <<'__VANTIX_FILE_5247220764973224356__'
import SwiftUI

enum VantixColors {
    static let graphite = Color(red: 0.025, green: 0.035, blue: 0.045)
    static let panel = Color(red: 0.045, green: 0.065, blue: 0.080)
    static let panelElevated = Color(red: 0.065, green: 0.085, blue: 0.105)
    static let border = Color.white.opacity(0.13)
    static let cyan = Color(red: 0.20, green: 0.88, blue: 1.00)
    static let teal = Color(red: 0.15, green: 0.78, blue: 0.72)
    static let amber = Color(red: 1.00, green: 0.66, blue: 0.18)
    static let critical = Color(red: 0.95, green: 0.26, blue: 0.30)
    static let success = Color(red: 0.30, green: 0.90, blue: 0.54)
    static let primaryText = Color.white.opacity(0.96)
    static let secondaryText = Color.white.opacity(0.62)
    static let tertiaryText = Color.white.opacity(0.38)
}
__VANTIX_FILE_5247220764973224356__

mkdir -p "$ROOT/VANTIX/Core/DesignSystem"
cat > "$ROOT/VANTIX/Core/DesignSystem/VantixMetrics.swift" <<'__VANTIX_FILE_3348050957587829303__'
import SwiftUI

enum VantixSpacing {
    static let xxs: CGFloat = 4
    static let xs: CGFloat = 6
    static let sm: CGFloat = 8
    static let md: CGFloat = 12
    static let lg: CGFloat = 16
    static let xl: CGFloat = 24
}

enum VantixRadius {
    static let control: CGFloat = 8
    static let panel: CGFloat = 10
}

enum VantixTypography {
    static let micro = Font.system(size: 9, weight: .semibold, design: .monospaced)
    static let caption = Font.system(size: 11, weight: .medium, design: .default)
    static let telemetry = Font.system(size: 12, weight: .medium, design: .monospaced)
    static let body = Font.system(size: 14, weight: .medium)
    static let title = Font.system(size: 20, weight: .bold)
}
__VANTIX_FILE_3348050957587829303__

mkdir -p "$ROOT/VANTIX/Core/Extensions"
cat > "$ROOT/VANTIX/Core/Extensions/Color+Intel.swift" <<'__VANTIX_FILE_415792489134004707__'
import SwiftUI

extension SeverityLevel {
    var color: Color {
        switch self {
        case .critical, .high: VantixColors.critical
        case .medium: VantixColors.amber
        case .low: VantixColors.cyan
        case .informational: VantixColors.teal
        }
    }
}

extension ConfidenceLevel {
    var color: Color {
        switch self {
        case .confirmed, .high: VantixColors.success
        case .medium: VantixColors.amber
        case .low, .unverified: VantixColors.secondaryText
        }
    }
}
__VANTIX_FILE_415792489134004707__

mkdir -p "$ROOT/VANTIX/Data/MockServices"
cat > "$ROOT/VANTIX/Data/MockServices/MockAircraftService.swift" <<'__VANTIX_FILE_3782172915767637409__'
import Foundation

struct MockAircraftService: IntelDomainService {
    let domain: IntelDomain = .air

    func fetchObjects() async -> [IntelObject] {
        MockFactory.makeObjects(
            count: 60,
            type: .aircraft,
            domain: .air,
            prefix: "AIR"
        )
    }

    func fetchInitialObservations(for objects: [IntelObject]) async -> [Observation] {
        MockFactory.initialObservations(
            objects: objects,
            source: MockFactory.aircraftSource,
            latitudeRange: 20...65,
            longitudeRange: -30...55,
            speedRange: 180...520,
            altitudeRange: 8000...40000
        )
    }

    func sourceRecords() -> [SourceRecord] {
        [MockFactory.aircraftSource]
    }
}
__VANTIX_FILE_3782172915767637409__

mkdir -p "$ROOT/VANTIX/Data/MockServices"
cat > "$ROOT/VANTIX/Data/MockServices/MockEventService.swift" <<'__VANTIX_FILE_7584770348451707584__'
import Foundation

struct MockEventService: IntelDomainService {
    let domain: IntelDomain = .environment

    func fetchObjects() async -> [IntelObject] {
        MockFactory.makeObjects(
            count: 20,
            type: .event,
            domain: .environment,
            prefix: "EVENT"
        )
    }

    func fetchInitialObservations(for objects: [IntelObject]) async -> [Observation] {
        MockFactory.initialObservations(
            objects: objects,
            source: MockFactory.eventSource,
            latitudeRange: -10...65,
            longitudeRange: -40...80,
            speedRange: 0...0,
            altitudeRange: nil
        )
    }

    func sourceRecords() -> [SourceRecord] {
        [MockFactory.eventSource]
    }
}
__VANTIX_FILE_7584770348451707584__

mkdir -p "$ROOT/VANTIX/Data/MockServices"
cat > "$ROOT/VANTIX/Data/MockServices/MockFacilityService.swift" <<'__VANTIX_FILE_4292535954615276159__'
import Foundation

struct MockFacilityService: IntelDomainService {
    let domain: IntelDomain = .land

    func fetchObjects() async -> [IntelObject] {
        MockFactory.makeObjects(
            count: 12,
            type: .facility,
            domain: .land,
            prefix: "SITE"
        )
    }

    func fetchInitialObservations(for objects: [IntelObject]) async -> [Observation] {
        MockFactory.initialObservations(
            objects: objects,
            source: MockFactory.facilitySource,
            latitudeRange: 10...60,
            longitudeRange: -20...70,
            speedRange: 0...0,
            altitudeRange: nil
        )
    }

    func sourceRecords() -> [SourceRecord] {
        [MockFactory.facilitySource]
    }
}
__VANTIX_FILE_4292535954615276159__

mkdir -p "$ROOT/VANTIX/Data/MockServices"
cat > "$ROOT/VANTIX/Data/MockServices/MockFactory.swift" <<'__VANTIX_FILE_7733692356027422842__'
import Foundation

enum MockFactory {
    static let aircraftSource = SourceRecord(
        id: UUID(uuidString: "10000000-0000-0000-0000-000000000001")!,
        name: "VANTIX ADS-B SIM",
        sourceType: "ADS-B",
        domain: .air,
        reliability: .high,
        status: .simulated,
        lastUpdated: .now
    )

    static let vesselSource = SourceRecord(
        id: UUID(uuidString: "10000000-0000-0000-0000-000000000002")!,
        name: "VANTIX AIS SIM",
        sourceType: "AIS",
        domain: .sea,
        reliability: .high,
        status: .simulated,
        lastUpdated: .now
    )

    static let satelliteSource = SourceRecord(
        id: UUID(uuidString: "10000000-0000-0000-0000-000000000003")!,
        name: "VANTIX ORBIT SIM",
        sourceType: "Orbital",
        domain: .space,
        reliability: .medium,
        status: .simulated,
        lastUpdated: .now
    )

    static let facilitySource = SourceRecord(
        id: UUID(uuidString: "10000000-0000-0000-0000-000000000004")!,
        name: "VANTIX GEO SIM",
        sourceType: "Geospatial",
        domain: .land,
        reliability: .confirmed,
        status: .simulated,
        lastUpdated: .now
    )

    static let eventSource = SourceRecord(
        id: UUID(uuidString: "10000000-0000-0000-0000-000000000005")!,
        name: "VANTIX EVENT SIM",
        sourceType: "Event",
        domain: .environment,
        reliability: .medium,
        status: .simulated,
        lastUpdated: .now
    )

    static func makeObjects(
        count: Int,
        type: IntelObjectType,
        domain: IntelDomain,
        prefix: String
    ) -> [IntelObject] {
        (0..<count).map { index in
            IntelObject(
                id: UUID(),
                type: type,
                domain: domain,
                name: "\(prefix)-\(String(format: "%03d", index + 1))",
                callsign: type == .aircraft ? "VX\(1200 + index)" : nil,
                description: "Simulated \(type.rawValue) object",
                status: type == .facility ? .stationary : .active,
                tags: ["SIMULATED", domain.rawValue.uppercased()],
                metadata: ["classification": "SIMULATED"],
                createdAt: .now,
                updatedAt: .now
            )
        }
    }

    static func initialObservations(
        objects: [IntelObject],
        source: SourceRecord,
        latitudeRange: ClosedRange<Double>,
        longitudeRange: ClosedRange<Double>,
        speedRange: ClosedRange<Double>,
        altitudeRange: ClosedRange<Double>? = nil
    ) -> [Observation] {
        objects.map { object in
            Observation(
                id: UUID(),
                objectID: object.id,
                timestamp: .now,
                latitude: Double.random(in: latitudeRange),
                longitude: Double.random(in: longitudeRange),
                altitude: altitudeRange.map { Double.random(in: $0) },
                depth: nil,
                speed: object.status == .stationary ? 0 : Double.random(in: speedRange),
                heading: Double.random(in: 0..<360),
                value: nil,
                sourceID: source.id,
                confidence: [.confirmed, .high, .medium].randomElement() ?? .high,
                metadata: ["simulated": "true"]
            )
        }
    }
}
__VANTIX_FILE_7733692356027422842__

mkdir -p "$ROOT/VANTIX/Data/MockServices"
cat > "$ROOT/VANTIX/Data/MockServices/MockSatelliteService.swift" <<'__VANTIX_FILE_2408307844154826324__'
import Foundation

struct MockSatelliteService: IntelDomainService {
    let domain: IntelDomain = .space

    func fetchObjects() async -> [IntelObject] {
        MockFactory.makeObjects(
            count: 10,
            type: .satellite,
            domain: .space,
            prefix: "SAT"
        )
    }

    func fetchInitialObservations(for objects: [IntelObject]) async -> [Observation] {
        MockFactory.initialObservations(
            objects: objects,
            source: MockFactory.satelliteSource,
            latitudeRange: -60...70,
            longitudeRange: -160...160,
            speedRange: 7000...17000,
            altitudeRange: 350000...1200000
        )
    }

    func sourceRecords() -> [SourceRecord] {
        [MockFactory.satelliteSource]
    }
}
__VANTIX_FILE_2408307844154826324__

mkdir -p "$ROOT/VANTIX/Data/MockServices"
cat > "$ROOT/VANTIX/Data/MockServices/MockVesselService.swift" <<'__VANTIX_FILE_1491915989075489232__'
import Foundation

struct MockVesselService: IntelDomainService {
    let domain: IntelDomain = .sea

    func fetchObjects() async -> [IntelObject] {
        MockFactory.makeObjects(
            count: 20,
            type: .vessel,
            domain: .sea,
            prefix: "VESSEL"
        )
    }

    func fetchInitialObservations(for objects: [IntelObject]) async -> [Observation] {
        MockFactory.initialObservations(
            objects: objects,
            source: MockFactory.vesselSource,
            latitudeRange: -10...60,
            longitudeRange: -45...75,
            speedRange: 5...24,
            altitudeRange: nil
        )
    }

    func sourceRecords() -> [SourceRecord] {
        [MockFactory.vesselSource]
    }
}
__VANTIX_FILE_1491915989075489232__

mkdir -p "$ROOT/VANTIX/Data/Repositories"
cat > "$ROOT/VANTIX/Data/Repositories/IntelRepository.swift" <<'__VANTIX_FILE_7126454487064582686__'
import Foundation
import Combine

@MainActor
final class IntelRepository: ObservableObject, IntelRepositoryProtocol {
    @Published private(set) var states: [ObjectState] = []

    private let services: [any IntelDomainService]
    private var objectsByID: [UUID: IntelObject] = [:]
    private var observationsByObjectID: [UUID: [Observation]] = [:]
    private var sourcesByID: [UUID: SourceRecord] = [:]

    init(services: [any IntelDomainService]) {
        self.services = services
    }

    var objectCount: Int { objectsByID.count }

    func load() async {
        var loadedObjects: [IntelObject] = []
        var loadedObservations: [Observation] = []

        for service in services {
            let objects = await service.fetchObjects()
            loadedObjects.append(contentsOf: objects)
            loadedObservations.append(contentsOf: await service.fetchInitialObservations(for: objects))

            for source in service.sourceRecords() {
                sourcesByID[source.id] = source
            }
        }

        objectsByID = Dictionary(uniqueKeysWithValues: loadedObjects.map { ($0.id, $0) })

        for observation in loadedObservations {
            observationsByObjectID[observation.objectID, default: []].append(observation)
        }

        rebuildStates()
    }

    func objectState(id: UUID) -> ObjectState? {
        states.first { $0.id == id }
    }

    func observations(for objectID: UUID) -> [Observation] {
        observationsByObjectID[objectID] ?? []
    }

    func append(_ observation: Observation) {
        observationsByObjectID[observation.objectID, default: []].append(observation)
        rebuildState(for: observation.objectID)
    }

    func source(id: UUID) -> SourceRecord? {
        sourcesByID[id]
    }

    private func rebuildStates() {
        states = objectsByID.values.compactMap { object in
            guard let observation = observationsByObjectID[object.id]?.max(by: { $0.timestamp < $1.timestamp }) else {
                return nil
            }

            return ObjectState(
                object: object,
                observation: observation,
                source: sourcesByID[observation.sourceID],
                severity: defaultSeverity(for: object)
            )
        }
        .sorted { $0.object.name < $1.object.name }
    }

    private func rebuildState(for objectID: UUID) {
        guard
            let object = objectsByID[objectID],
            let observation = observationsByObjectID[objectID]?.max(by: { $0.timestamp < $1.timestamp })
        else { return }

        let newState = ObjectState(
            object: object,
            observation: observation,
            source: sourcesByID[observation.sourceID],
            severity: defaultSeverity(for: object)
        )

        if let index = states.firstIndex(where: { $0.id == objectID }) {
            states[index] = newState
        } else {
            states.append(newState)
        }
    }

    private func defaultSeverity(for object: IntelObject) -> SeverityLevel {
        switch object.type {
        case .alert: .high
        case .event: .medium
        default: .informational
        }
    }
}
__VANTIX_FILE_7126454487064582686__

mkdir -p "$ROOT/VANTIX/Data/Simulation"
cat > "$ROOT/VANTIX/Data/Simulation/SimulationEngine.swift" <<'__VANTIX_FILE_7549280009517352651__'
import Foundation

@MainActor
final class SimulationEngine {
    private weak var repository: IntelRepository?
    private var task: Task<Void, Never>?

    init(repository: IntelRepository) {
        self.repository = repository
    }

    func start() {
        guard task == nil else { return }

        task = Task { [weak self] in
            while !Task.isCancelled {
                try? await Task.sleep(for: .milliseconds(900))
                guard let self, let repository = self.repository else { continue }

                let moving = repository.states
                    .filter { $0.object.type == .aircraft || $0.object.type == .vessel }
                    .prefix(24)

                for state in moving {
                    let heading = state.heading ?? 0
                    let speed = state.speed ?? 0
                    let distanceDegrees = max(speed, 1) / 90000.0

                    let radians = heading * .pi / 180
                    let nextLat = state.coordinate.latitude + cos(radians) * distanceDegrees
                    let nextLon = state.coordinate.longitude + sin(radians) * distanceDegrees

                    let observation = Observation(
                        id: UUID(),
                        objectID: state.id,
                        timestamp: .now,
                        latitude: nextLat,
                        longitude: nextLon,
                        altitude: state.altitude,
                        depth: state.depth,
                        speed: speed + Double.random(in: -2...2),
                        heading: (heading + Double.random(in: -1.5...1.5)).truncatingRemainder(dividingBy: 360),
                        value: nil,
                        sourceID: state.observation.sourceID,
                        confidence: state.confidence,
                        metadata: ["simulated": "true"]
                    )

                    repository.append(observation)
                }
            }
        }
    }

    func stop() {
        task?.cancel()
        task = nil
    }

    deinit {
        task?.cancel()
    }
}
__VANTIX_FILE_7549280009517352651__

mkdir -p "$ROOT/VANTIX/Domain/Models"
cat > "$ROOT/VANTIX/Domain/Models/Enums.swift" <<'__VANTIX_FILE_6654799696311496__'
import Foundation

enum ConfidenceLevel: String, Codable, CaseIterable, Sendable {
    case confirmed
    case high
    case medium
    case low
    case unverified
}

enum SeverityLevel: String, Codable, CaseIterable, Sendable {
    case critical
    case high
    case medium
    case low
    case informational
}
__VANTIX_FILE_6654799696311496__

mkdir -p "$ROOT/VANTIX/Domain/Models"
cat > "$ROOT/VANTIX/Domain/Models/IntelDomain.swift" <<'__VANTIX_FILE_6487547766941013003__'
import Foundation

enum IntelDomain: String, Codable, CaseIterable, Sendable {
    case air
    case land
    case sea
    case subsurface
    case space
    case rf
    case cyber
    case environment
}
__VANTIX_FILE_6487547766941013003__

mkdir -p "$ROOT/VANTIX/Domain/Models"
cat > "$ROOT/VANTIX/Domain/Models/IntelObject.swift" <<'__VANTIX_FILE_5532574740694717371__'
import Foundation
import CoreLocation

enum IntelObjectType: String, Codable, CaseIterable, Sendable {
    case aircraft
    case vessel
    case satellite
    case facility
    case event
    case alert
    case buoy
    case tower
    case sensor
}

enum IntelStatus: String, Codable, Sendable {
    case active
    case inTransit
    case stationary
    case degraded
    case offline
    case unknown
}

struct IntelObject: Identifiable, Codable, Hashable, Sendable {
    let id: UUID
    let type: IntelObjectType
    let domain: IntelDomain
    var name: String
    var callsign: String?
    var description: String?
    var status: IntelStatus
    var tags: [String]
    var metadata: [String: String]
    var createdAt: Date
    var updatedAt: Date
}
__VANTIX_FILE_5532574740694717371__

mkdir -p "$ROOT/VANTIX/Domain/Models"
cat > "$ROOT/VANTIX/Domain/Models/ObjectState.swift" <<'__VANTIX_FILE_7470033242809700483__'
import Foundation
import CoreLocation

struct ObjectState: Identifiable, Hashable, Sendable {
    var id: UUID { object.id }

    let object: IntelObject
    let observation: Observation
    let source: SourceRecord?
    let severity: SeverityLevel

    var coordinate: CLLocationCoordinate2D { observation.coordinate }
    var altitude: Double? { observation.altitude }
    var depth: Double? { observation.depth }
    var speed: Double? { observation.speed }
    var heading: Double? { observation.heading }
    var confidence: ConfidenceLevel { observation.confidence }
    var timestamp: Date { observation.timestamp }
}
__VANTIX_FILE_7470033242809700483__

mkdir -p "$ROOT/VANTIX/Domain/Models"
cat > "$ROOT/VANTIX/Domain/Models/Observation.swift" <<'__VANTIX_FILE_5555440702871881823__'
import Foundation
import CoreLocation

struct Observation: Identifiable, Codable, Hashable, Sendable {
    let id: UUID
    let objectID: UUID
    let timestamp: Date
    let latitude: Double
    let longitude: Double
    let altitude: Double?
    let depth: Double?
    let speed: Double?
    let heading: Double?
    let value: Double?
    let sourceID: UUID
    let confidence: ConfidenceLevel
    let metadata: [String: String]

    var coordinate: CLLocationCoordinate2D {
        CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    }
}
__VANTIX_FILE_5555440702871881823__

mkdir -p "$ROOT/VANTIX/Domain/Models"
cat > "$ROOT/VANTIX/Domain/Models/SelectionState.swift" <<'__VANTIX_FILE_8803839281850053372__'
import Foundation

struct SelectionState: Equatable {
    var selectedObjectID: UUID?
    var focusedObjectID: UUID?
    var inspectorPresentationState: InspectorPresentationState = .collapsed
}

enum InspectorPresentationState: Equatable {
    case collapsed
    case medium
    case expanded
}
__VANTIX_FILE_8803839281850053372__

mkdir -p "$ROOT/VANTIX/Domain/Models"
cat > "$ROOT/VANTIX/Domain/Models/SourceRecord.swift" <<'__VANTIX_FILE_8521796293569204883__'
import Foundation

enum SourceReliability: String, Codable, Sendable {
    case confirmed
    case high
    case medium
    case low
    case unknown
}

enum SourceStatus: String, Codable, Sendable {
    case online
    case degraded
    case delayed
    case offline
    case simulated
}

struct SourceRecord: Identifiable, Codable, Hashable, Sendable {
    let id: UUID
    let name: String
    let sourceType: String
    let domain: IntelDomain
    let reliability: SourceReliability
    let status: SourceStatus
    let lastUpdated: Date
}
__VANTIX_FILE_8521796293569204883__

mkdir -p "$ROOT/VANTIX/Domain/Protocols"
cat > "$ROOT/VANTIX/Domain/Protocols/IntelDomainService.swift" <<'__VANTIX_FILE_4450766424802247258__'
import Foundation

protocol IntelDomainService: Sendable {
    var domain: IntelDomain { get }
    func fetchObjects() async -> [IntelObject]
    func fetchInitialObservations(for objects: [IntelObject]) async -> [Observation]
    func sourceRecords() -> [SourceRecord]
}
__VANTIX_FILE_4450766424802247258__

mkdir -p "$ROOT/VANTIX/Domain/Protocols"
cat > "$ROOT/VANTIX/Domain/Protocols/IntelRepositoryProtocol.swift" <<'__VANTIX_FILE_622589514603697063__'
import Foundation

@MainActor
protocol IntelRepositoryProtocol: AnyObject {
    var states: [ObjectState] { get }
    var objectCount: Int { get }

    func load() async
    func objectState(id: UUID) -> ObjectState?
    func append(_ observation: Observation)
    func observations(for objectID: UUID) -> [Observation]
}
__VANTIX_FILE_622589514603697063__

mkdir -p "$ROOT/VANTIX/Features/Alerts/Views"
cat > "$ROOT/VANTIX/Features/Alerts/Views/AlertsPlaceholderView.swift" <<'__VANTIX_FILE_7169338613177442747__'
import SwiftUI

struct AlertsPlaceholderView: View {
    var body: some View {
        ZStack {
            VantixColors.graphite.ignoresSafeArea()

            VStack(spacing: 14) {
                Image(systemName: "bell.fill")
                    .font(.system(size: 28, weight: .semibold))
                    .foregroundStyle(VantixColors.cyan)

                Text("ALERTS")
                    .font(VantixTypography.title)
                    .foregroundStyle(VantixColors.primaryText)

                Text("Alert triage, anomaly workflows, and geofence triggers will be added after temporal intelligence.")
                    .font(VantixTypography.body)
                    .foregroundStyle(VantixColors.secondaryText)
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: 310)

                Text("SIMULATED DATA")
                    .font(VantixTypography.micro)
                    .foregroundStyle(VantixColors.tertiaryText)
                    .padding(.top, 8)
            }
        }
    }
}
__VANTIX_FILE_7169338613177442747__

mkdir -p "$ROOT/VANTIX/Features/Graph/Views"
cat > "$ROOT/VANTIX/Features/Graph/Views/GraphPlaceholderView.swift" <<'__VANTIX_FILE_48353054162110803__'
import SwiftUI

struct GraphPlaceholderView: View {
    var body: some View {
        ZStack {
            VantixColors.graphite.ignoresSafeArea()

            VStack(spacing: 14) {
                Image(systemName: "point.3.connected.trianglepath.dotted")
                    .font(.system(size: 28, weight: .semibold))
                    .foregroundStyle(VantixColors.cyan)

                Text("GRAPH")
                    .font(VantixTypography.title)
                    .foregroundStyle(VantixColors.primaryText)

                Text("Entity relationships and correlation graph are staged for a later milestone.")
                    .font(VantixTypography.body)
                    .foregroundStyle(VantixColors.secondaryText)
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: 310)

                Text("SIMULATED DATA")
                    .font(VantixTypography.micro)
                    .foregroundStyle(VantixColors.tertiaryText)
                    .padding(.top, 8)
            }
        }
    }
}
__VANTIX_FILE_48353054162110803__

mkdir -p "$ROOT/VANTIX/Features/Intel/Views"
cat > "$ROOT/VANTIX/Features/Intel/Views/IntelPlaceholderView.swift" <<'__VANTIX_FILE_7241385860242985762__'
import SwiftUI

struct IntelPlaceholderView: View {
    var body: some View {
        ZStack {
            VantixColors.graphite.ignoresSafeArea()

            VStack(spacing: 14) {
                Image(systemName: "waveform.path.ecg.rectangle")
                    .font(.system(size: 28, weight: .semibold))
                    .foregroundStyle(VantixColors.cyan)

                Text("INTEL")
                    .font(VantixTypography.title)
                    .foregroundStyle(VantixColors.primaryText)

                Text("Situations, event feeds, source health, and sensor intelligence arrive in Prompt 3.")
                    .font(VantixTypography.body)
                    .foregroundStyle(VantixColors.secondaryText)
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: 310)

                Text("SIMULATED DATA")
                    .font(VantixTypography.micro)
                    .foregroundStyle(VantixColors.tertiaryText)
                    .padding(.top, 8)
            }
        }
    }
}
__VANTIX_FILE_7241385860242985762__

mkdir -p "$ROOT/VANTIX/Features/Map/Components"
cat > "$ROOT/VANTIX/Features/Map/Components/BottomNavigation.swift" <<'__VANTIX_FILE_5774596162404402083__'
import SwiftUI

struct BottomNavigation: View {
    @Binding var selectedTab: AppTab

    var body: some View {
        HStack(spacing: 0) {
            ForEach(AppTab.allCases) { tab in
                Button {
                    selectedTab = tab
                } label: {
                    VStack(spacing: 3) {
                        Image(systemName: tab.icon)
                            .font(.system(size: 15, weight: .semibold))
                        Text(tab.rawValue)
                            .font(.system(size: 8, weight: .bold, design: .monospaced))
                    }
                    .foregroundStyle(selectedTab == tab ? VantixColors.cyan : VantixColors.secondaryText)
                    .frame(maxWidth: .infinity)
                    .frame(height: 51)
                }
                .buttonStyle(.plain)
            }
        }
        .background(VantixColors.graphite.opacity(0.96))
        .overlay(alignment: .top) {
            Rectangle()
                .fill(VantixColors.border)
                .frame(height: 1)
        }
    }
}
__VANTIX_FILE_5774596162404402083__

mkdir -p "$ROOT/VANTIX/Features/Map/Components"
cat > "$ROOT/VANTIX/Features/Map/Components/FloatingMapControls.swift" <<'__VANTIX_FILE_4968176401399235664__'
import SwiftUI

struct FloatingMapControls: View {
    let onLayers: () -> Void
    let onTimeline: () -> Void
    let onAI: () -> Void
    let onRecenter: () -> Void

    var body: some View {
        VStack(spacing: 7) {
            ControlButton(icon: "square.3.layers.3d", label: "LAYERS", action: onLayers)
            ControlButton(icon: "clock.arrow.circlepath", label: "TIME", action: onTimeline)
            ControlButton(icon: "sparkles", label: "AI", tint: .purple, action: onAI)
            ControlButton(icon: "scope", label: "CENTER", action: onRecenter)
        }
    }
}

private struct ControlButton: View {
    let icon: String
    let label: String
    var tint: Color = VantixColors.cyan
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 3) {
                Image(systemName: icon)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundStyle(tint)
                Text(label)
                    .font(.system(size: 7, weight: .bold, design: .monospaced))
                    .foregroundStyle(VantixColors.secondaryText)
            }
            .frame(width: 52, height: 48)
            .background(VantixColors.panel.opacity(0.94))
            .overlay {
                RoundedRectangle(cornerRadius: VantixRadius.control)
                    .stroke(VantixColors.border, lineWidth: 1)
            }
        }
        .buttonStyle(.plain)
    }
}
__VANTIX_FILE_4968176401399235664__

mkdir -p "$ROOT/VANTIX/Features/Map/Components"
cat > "$ROOT/VANTIX/Features/Map/Components/MapPlaceholderPanel.swift" <<'__VANTIX_FILE_1490494016303141141__'
import SwiftUI

struct MapPlaceholderPanel: View {
    let title: String
    let bodyText: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(VantixTypography.caption)
                .foregroundStyle(VantixColors.cyan)
            Text(bodyText)
                .font(VantixTypography.caption)
                .foregroundStyle(VantixColors.secondaryText)
        }
        .padding(12)
        .frame(maxWidth: 260, alignment: .leading)
        .background(VantixColors.panel.opacity(0.97))
        .overlay {
            RoundedRectangle(cornerRadius: VantixRadius.panel)
                .stroke(VantixColors.border, lineWidth: 1)
        }
    }
}
__VANTIX_FILE_1490494016303141141__

mkdir -p "$ROOT/VANTIX/Features/Map/Components"
cat > "$ROOT/VANTIX/Features/Map/Components/TopStatusBar.swift" <<'__VANTIX_FILE_1455864583363775023__'
import SwiftUI

struct TopStatusBar: View {
    @Binding var searchText: String

    var body: some View {
        VStack(spacing: 8) {
            HStack(spacing: 8) {
                HStack(spacing: 7) {
                    Image(systemName: "triangle.fill")
                        .font(.system(size: 12))
                        .foregroundStyle(VantixColors.cyan)
                    Text("VANTIX")
                        .font(.system(size: 17, weight: .black, design: .rounded))
                        .foregroundStyle(VantixColors.primaryText)
                }

                HStack(spacing: 6) {
                    Image(systemName: "magnifyingglass")
                        .foregroundStyle(VantixColors.secondaryText)
                    TextField("Search assets, IDs…", text: $searchText)
                        .font(VantixTypography.caption)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                }
                .padding(.horizontal, 10)
                .frame(height: 34)
                .background(VantixColors.panel.opacity(0.93))
                .overlay {
                    RoundedRectangle(cornerRadius: VantixRadius.control)
                        .stroke(VantixColors.border, lineWidth: 1)
                }
            }

            HStack(spacing: 0) {
                StatusCell(label: "SITUATION", value: "ELEVATED", valueColor: VantixColors.amber)
                Divider().overlay(VantixColors.border)
                StatusCell(label: "OBJECTS", value: "122", valueColor: VantixColors.cyan)
                Divider().overlay(VantixColors.border)
                StatusCell(label: "SYSTEM", value: "OPERATIONAL", valueColor: VantixColors.success)
            }
            .frame(height: 42)
            .background(VantixColors.panel.opacity(0.92))
            .overlay {
                RoundedRectangle(cornerRadius: VantixRadius.control)
                    .stroke(VantixColors.border, lineWidth: 1)
            }
        }
        .padding(.horizontal, 10)
    }
}

private struct StatusCell: View {
    let label: String
    let value: String
    let valueColor: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label)
                .font(VantixTypography.micro)
                .foregroundStyle(VantixColors.tertiaryText)
            Text(value)
                .font(.system(size: 10, weight: .bold, design: .monospaced))
                .foregroundStyle(valueColor)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 8)
    }
}
__VANTIX_FILE_1455864583363775023__

mkdir -p "$ROOT/VANTIX/Features/Map/MapKit"
cat > "$ROOT/VANTIX/Features/Map/MapKit/IntelAnnotation.swift" <<'__VANTIX_FILE_3994400175658749371__'
import Foundation
import MapKit

final class IntelAnnotation: NSObject, MKAnnotation {
    let objectID: UUID
    let domain: IntelDomain
    let type: IntelObjectType
    var coordinate: CLLocationCoordinate2D
    var heading: Double
    var status: IntelStatus
    var severity: SeverityLevel
    var confidence: ConfidenceLevel
    let title: String?

    init(state: ObjectState) {
        self.objectID = state.id
        self.domain = state.object.domain
        self.type = state.object.type
        self.coordinate = state.coordinate
        self.heading = state.heading ?? 0
        self.status = state.object.status
        self.severity = state.severity
        self.confidence = state.confidence
        self.title = state.object.name
        super.init()
    }

    func apply(_ state: ObjectState) {
        coordinate = state.coordinate
        heading = state.heading ?? 0
        status = state.object.status
        severity = state.severity
        confidence = state.confidence
    }
}
__VANTIX_FILE_3994400175658749371__

mkdir -p "$ROOT/VANTIX/Features/Map/MapKit"
cat > "$ROOT/VANTIX/Features/Map/MapKit/IntelAnnotationView.swift" <<'__VANTIX_FILE_8698960824757960199__'
import UIKit
import MapKit

final class IntelAnnotationView: MKAnnotationView {
    static let reuseIdentifier = "IntelAnnotationView"

    private let container = UIView()
    private let iconView = UIImageView()

    override init(annotation: MKAnnotation?, reuseIdentifier: String?) {
        super.init(annotation: annotation, reuseIdentifier: reuseIdentifier)
        collisionMode = .circle
        displayPriority = .defaultHigh
        clusteringIdentifier = "vantix.intel"
        centerOffset = CGPoint(x: 0, y: 0)

        container.translatesAutoresizingMaskIntoConstraints = false
        iconView.translatesAutoresizingMaskIntoConstraints = false

        addSubview(container)
        container.addSubview(iconView)

        NSLayoutConstraint.activate([
            container.widthAnchor.constraint(equalToConstant: 30),
            container.heightAnchor.constraint(equalToConstant: 30),
            container.centerXAnchor.constraint(equalTo: centerXAnchor),
            container.centerYAnchor.constraint(equalTo: centerYAnchor),

            iconView.widthAnchor.constraint(equalToConstant: 18),
            iconView.heightAnchor.constraint(equalToConstant: 18),
            iconView.centerXAnchor.constraint(equalTo: container.centerXAnchor),
            iconView.centerYAnchor.constraint(equalTo: container.centerYAnchor)
        ])

        frame = CGRect(x: 0, y: 0, width: 30, height: 30)
        container.layer.cornerRadius = 7
        container.layer.borderWidth = 1
        container.backgroundColor = UIColor(red: 0.02, green: 0.05, blue: 0.07, alpha: 0.90)
        iconView.contentMode = .scaleAspectFit
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override var annotation: MKAnnotation? {
        didSet { configure() }
    }

    func configure() {
        guard let intel = annotation as? IntelAnnotation else { return }

        iconView.image = UIImage(systemName: symbol(for: intel.type))?.withRenderingMode(.alwaysTemplate)
        iconView.tintColor = color(for: intel)
        container.layer.borderColor = color(for: intel).withAlphaComponent(0.55).cgColor

        if intel.type == .aircraft || intel.type == .vessel {
            iconView.transform = CGAffineTransform(rotationAngle: intel.heading * .pi / 180)
        } else {
            iconView.transform = .identity
        }
    }

    private func symbol(for type: IntelObjectType) -> String {
        switch type {
        case .aircraft: "airplane"
        case .vessel: "ferry.fill"
        case .satellite: "antenna.radiowaves.left.and.right"
        case .facility: "building.2.fill"
        case .event: "exclamationmark.triangle.fill"
        case .alert: "diamond.fill"
        case .buoy: "water.waves"
        case .tower: "dot.radiowaves.left.and.right"
        case .sensor: "sensor.fill"
        }
    }

    private func color(for annotation: IntelAnnotation) -> UIColor {
        switch annotation.severity {
        case .critical, .high:
            UIColor(red: 0.95, green: 0.26, blue: 0.30, alpha: 1)
        case .medium:
            UIColor(red: 1.00, green: 0.66, blue: 0.18, alpha: 1)
        case .low, .informational:
            switch annotation.domain {
            case .air, .space: UIColor(red: 0.20, green: 0.88, blue: 1.00, alpha: 1)
            case .sea, .subsurface: UIColor(red: 0.15, green: 0.78, blue: 0.72, alpha: 1)
            default: UIColor(red: 0.55, green: 0.80, blue: 0.92, alpha: 1)
            }
        }
    }
}
__VANTIX_FILE_8698960824757960199__

mkdir -p "$ROOT/VANTIX/Features/Map/MapKit"
cat > "$ROOT/VANTIX/Features/Map/MapKit/VantixMapView.swift" <<'__VANTIX_FILE_666788663169453659__'
import SwiftUI
import MapKit

struct VantixMapView: UIViewRepresentable {
    let states: [ObjectState]
    @Binding var selectedObjectID: UUID?
    let focusObjectID: UUID?
    let recenterToken: Int

    func makeCoordinator() -> Coordinator {
        Coordinator(parent: self)
    }

    func makeUIView(context: Context) -> MKMapView {
        let map = MKMapView(frame: .zero)
        map.delegate = context.coordinator
        map.overrideUserInterfaceStyle = .dark
        map.showsCompass = false
        map.showsScale = false
        map.pointOfInterestFilter = .excludingAll
        map.isRotateEnabled = true
        map.isPitchEnabled = true

        let configuration = MKStandardMapConfiguration(elevationStyle: .realistic)
        configuration.emphasisStyle = .muted
        map.preferredConfiguration = configuration

        map.register(
            IntelAnnotationView.self,
            forAnnotationViewWithReuseIdentifier: IntelAnnotationView.reuseIdentifier
        )
        map.register(
            MKMarkerAnnotationView.self,
            forAnnotationViewWithReuseIdentifier: MKMapViewDefaultClusterAnnotationViewReuseIdentifier
        )

        map.setCamera(defaultCamera(), animated: false)
        context.coordinator.sync(states, on: map)
        return map
    }

    func updateUIView(_ map: MKMapView, context: Context) {
        context.coordinator.parent = self
        context.coordinator.sync(states, on: map)

        if context.coordinator.lastRecenterToken != recenterToken {
            context.coordinator.lastRecenterToken = recenterToken
            map.setCamera(defaultCamera(), animated: true)
        }

        if let focusObjectID,
           context.coordinator.lastFocusedObjectID != focusObjectID,
           let annotation = context.coordinator.annotationsByID[focusObjectID] {
            context.coordinator.lastFocusedObjectID = focusObjectID
            map.setCenter(annotation.coordinate, animated: true)
            map.selectAnnotation(annotation, animated: true)
        }
    }

    private func defaultCamera() -> MKMapCamera {
        MKMapCamera(
            lookingAtCenter: CLLocationCoordinate2D(latitude: 34, longitude: 16),
            fromDistance: 11_000_000,
            pitch: 18,
            heading: 0
        )
    }

    final class Coordinator: NSObject, MKMapViewDelegate {
        var parent: VantixMapView
        var annotationsByID: [UUID: IntelAnnotation] = [:]
        var lastRecenterToken = 0
        var lastFocusedObjectID: UUID?

        init(parent: VantixMapView) {
            self.parent = parent
        }

        func sync(_ states: [ObjectState], on map: MKMapView) {
            let incomingIDs = Set(states.map(\.id))
            let stale = annotationsByID.filter { !incomingIDs.contains($0.key) }

            if !stale.isEmpty {
                map.removeAnnotations(Array(stale.values))
                for id in stale.keys { annotationsByID.removeValue(forKey: id) }
            }

            var additions: [IntelAnnotation] = []

            for state in states {
                if let annotation = annotationsByID[state.id] {
                    annotation.apply(state)
                    if let view = map.view(for: annotation) as? IntelAnnotationView {
                        view.configure()
                    }
                } else {
                    let annotation = IntelAnnotation(state: state)
                    annotationsByID[state.id] = annotation
                    additions.append(annotation)
                }
            }

            if !additions.isEmpty {
                map.addAnnotations(additions)
            }
        }

        func mapView(_ mapView: MKMapView, viewFor annotation: MKAnnotation) -> MKAnnotationView? {
            if let cluster = annotation as? MKClusterAnnotation {
                let view = mapView.dequeueReusableAnnotationView(
                    withIdentifier: MKMapViewDefaultClusterAnnotationViewReuseIdentifier,
                    for: cluster
                ) as! MKMarkerAnnotationView
                view.markerTintColor = UIColor(red: 0.08, green: 0.52, blue: 0.64, alpha: 0.92)
                view.glyphText = "\(cluster.memberAnnotations.count)"
                view.glyphTintColor = .white
                view.displayPriority = .defaultHigh
                return view
            }

            guard annotation is IntelAnnotation else { return nil }
            let view = mapView.dequeueReusableAnnotationView(
                withIdentifier: IntelAnnotationView.reuseIdentifier,
                for: annotation
            ) as! IntelAnnotationView
            view.configure()
            return view
        }

        func mapView(_ mapView: MKMapView, didSelect view: MKAnnotationView) {
            if let cluster = view.annotation as? MKClusterAnnotation {
                mapView.showAnnotations(cluster.memberAnnotations, animated: true)
                return
            }

            guard let annotation = view.annotation as? IntelAnnotation else { return }
            parent.selectedObjectID = annotation.objectID

            let camera = MKMapCamera(
                lookingAtCenter: annotation.coordinate,
                fromDistance: max(mapView.camera.centerCoordinateDistance * 0.65, 45_000),
                pitch: max(mapView.camera.pitch, 28),
                heading: mapView.camera.heading
            )
            mapView.setCamera(camera, animated: true)
        }
    }
}
__VANTIX_FILE_666788663169453659__

mkdir -p "$ROOT/VANTIX/Features/Map/ViewModels"
cat > "$ROOT/VANTIX/Features/Map/ViewModels/MapViewModel.swift" <<'__VANTIX_FILE_1333497653419313490__'
import Foundation
import Combine

@MainActor
final class MapViewModel: ObservableObject {
    @Published var recenterToken = 0
    @Published var showLayers = false
    @Published var showTimeline = false
    @Published var showAI = false
    @Published var searchText = ""

    func recenter() {
        recenterToken += 1
    }
}
__VANTIX_FILE_1333497653419313490__

mkdir -p "$ROOT/VANTIX/Features/Map/Views"
cat > "$ROOT/VANTIX/Features/Map/Views/MainMapView.swift" <<'__VANTIX_FILE_5269904595234052855__'
import SwiftUI

struct MainMapView: View {
    @EnvironmentObject private var environment: AppEnvironment
    @StateObject private var viewModel = MapViewModel()

    private var selectedState: ObjectState? {
        guard let id = environment.selection.selectedObjectID else { return nil }
        return environment.repository.objectState(id: id)
    }

    var body: some View {
        ZStack {
            VantixMapView(
                states: filteredStates,
                selectedObjectID: Binding(
                    get: { environment.selection.selectedObjectID },
                    set: { newValue in
                        environment.selection.selectedObjectID = newValue
                        environment.selection.focusedObjectID = newValue
                    }
                ),
                focusObjectID: environment.selection.focusedObjectID,
                recenterToken: viewModel.recenterToken
            )
            .ignoresSafeArea()

            LinearGradient(
                colors: [VantixColors.graphite.opacity(0.62), .clear, VantixColors.graphite.opacity(0.38)],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()
            .allowsHitTesting(false)

            VStack {
                TopStatusBar(searchText: $viewModel.searchText)
                    .padding(.top, 4)

                Spacer()

                HStack {
                    Spacer()
                    FloatingMapControls(
                        onLayers: { viewModel.showLayers.toggle() },
                        onTimeline: { viewModel.showTimeline.toggle() },
                        onAI: { viewModel.showAI.toggle() },
                        onRecenter: { viewModel.recenter() }
                    )
                    .padding(.trailing, 10)
                    .padding(.bottom, 76)
                }
            }

            if viewModel.showLayers {
                VStack {
                    Spacer()
                    HStack {
                        MapPlaceholderPanel(
                            title: "LAYERS",
                            bodyText: "Prompt 1 foundation ready. Domain layers arrive in Prompt 3."
                        )
                        Spacer()
                    }
                    .padding(.leading, 10)
                    .padding(.bottom, 74)
                }
            }

            VStack {
                Spacer()
                Text("SIMULATED DATA")
                    .font(VantixTypography.micro)
                    .foregroundStyle(VantixColors.tertiaryText)
                    .padding(.bottom, 58)
            }
        }
        .sheet(item: Binding(
            get: { selectedState },
            set: { _ in
                environment.selection.selectedObjectID = nil
                environment.selection.focusedObjectID = nil
            }
        )) { state in
            ObjectInspectorView(state: state)
                .presentationDetents([.fraction(0.22), .medium, .large])
                .presentationDragIndicator(.hidden)
                .presentationBackground(VantixColors.graphite)
        }
    }

    private var filteredStates: [ObjectState] {
        let query = viewModel.searchText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !query.isEmpty else { return environment.repository.states }

        return environment.repository.states.filter {
            $0.object.name.localizedCaseInsensitiveContains(query) ||
            ($0.object.callsign?.localizedCaseInsensitiveContains(query) ?? false) ||
            $0.object.type.rawValue.localizedCaseInsensitiveContains(query)
        }
    }
}
__VANTIX_FILE_5269904595234052855__

mkdir -p "$ROOT/VANTIX/Features/Map/Views"
cat > "$ROOT/VANTIX/Features/Map/Views/ObjectInspectorView.swift" <<'__VANTIX_FILE_8099278546867507530__'
import SwiftUI

struct ObjectInspectorView: View {
    let state: ObjectState

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Capsule()
                    .fill(VantixColors.tertiaryText)
                    .frame(width: 34, height: 4)
                    .frame(maxWidth: .infinity)

                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(state.object.name)
                            .font(VantixTypography.title)
                            .foregroundStyle(VantixColors.primaryText)

                        HStack(spacing: 7) {
                            Text(state.object.type.rawValue.uppercased())
                            Text("•")
                            Text(state.object.domain.rawValue.uppercased())
                        }
                        .font(VantixTypography.micro)
                        .foregroundStyle(VantixColors.secondaryText)
                    }

                    Spacer()

                    ConfidenceBadge(level: state.confidence)
                }

                Divider().overlay(VantixColors.border)

                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                    TelemetryCell(label: "STATUS", value: state.object.status.rawValue.uppercased())
                    TelemetryCell(label: "LAST UPDATE", value: state.timestamp.formatted(date: .omitted, time: .standard))
                    TelemetryCell(label: "LATITUDE", value: String(format: "%.4f°", state.coordinate.latitude))
                    TelemetryCell(label: "LONGITUDE", value: String(format: "%.4f°", state.coordinate.longitude))
                    TelemetryCell(label: "ALTITUDE", value: state.altitude.map { String(format: "%.0f ft", $0) } ?? "—")
                    TelemetryCell(label: "SPEED", value: state.speed.map { String(format: "%.0f kts", $0) } ?? "—")
                    TelemetryCell(label: "HEADING", value: state.heading.map { String(format: "%.0f°", $0) } ?? "—")
                    TelemetryCell(label: "SOURCE", value: state.source?.sourceType ?? "SIM")
                }

                HStack(spacing: 8) {
                    ActionButton(title: "TRACK", icon: "point.topleft.down.to.point.bottomright.curvepath")
                    ActionButton(title: "RELATIONSHIPS", icon: "point.3.connected.trianglepath.dotted")
                    ActionButton(title: "ANALYZE", icon: "sparkles")
                }

                Text("SIMULATED DATA")
                    .font(VantixTypography.micro)
                    .foregroundStyle(VantixColors.tertiaryText)
                    .frame(maxWidth: .infinity)
                    .padding(.top, 4)
            }
            .padding(16)
        }
        .background(VantixColors.graphite)
    }
}

private struct TelemetryCell: View {
    let label: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(label)
                .font(VantixTypography.micro)
                .foregroundStyle(VantixColors.tertiaryText)
            Text(value)
                .font(VantixTypography.telemetry)
                .foregroundStyle(VantixColors.primaryText)
                .lineLimit(1)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

private struct ConfidenceBadge: View {
    let level: ConfidenceLevel

    var body: some View {
        Text(level.rawValue.uppercased())
            .font(VantixTypography.micro)
            .foregroundStyle(level.color)
            .padding(.horizontal, 8)
            .padding(.vertical, 5)
            .background(level.color.opacity(0.10))
            .overlay {
                RoundedRectangle(cornerRadius: 6)
                    .stroke(level.color.opacity(0.45), lineWidth: 1)
            }
    }
}

private struct ActionButton: View {
    let title: String
    let icon: String

    var body: some View {
        Button {} label: {
            VStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.system(size: 13, weight: .semibold))
                Text(title)
                    .font(.system(size: 7, weight: .bold, design: .monospaced))
            }
            .foregroundStyle(VantixColors.cyan)
            .frame(maxWidth: .infinity)
            .frame(height: 54)
            .background(VantixColors.panel)
            .overlay {
                RoundedRectangle(cornerRadius: VantixRadius.control)
                    .stroke(VantixColors.border, lineWidth: 1)
            }
        }
        .buttonStyle(.plain)
    }
}
__VANTIX_FILE_8099278546867507530__

mkdir -p "$ROOT/VANTIX/Features/More/Views"
cat > "$ROOT/VANTIX/Features/More/Views/MorePlaceholderView.swift" <<'__VANTIX_FILE_2191407291354549511__'
import SwiftUI

struct MorePlaceholderView: View {
    var body: some View {
        ZStack {
            VantixColors.graphite.ignoresSafeArea()

            VStack(spacing: 14) {
                Image(systemName: "ellipsis")
                    .font(.system(size: 28, weight: .semibold))
                    .foregroundStyle(VantixColors.cyan)

                Text("MORE")
                    .font(VantixTypography.title)
                    .foregroundStyle(VantixColors.primaryText)

                Text("Settings, data sources, permissions, diagnostics, and enterprise controls.")
                    .font(VantixTypography.body)
                    .foregroundStyle(VantixColors.secondaryText)
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: 310)

                Text("SIMULATED DATA")
                    .font(VantixTypography.micro)
                    .foregroundStyle(VantixColors.tertiaryText)
                    .padding(.top, 8)
            }
        }
    }
}
__VANTIX_FILE_2191407291354549511__

mkdir -p "$ROOT/VANTIX/Resources/Assets.xcassets/AppIcon.appiconset"
cat > "$ROOT/VANTIX/Resources/Assets.xcassets/AppIcon.appiconset/Contents.json" <<'__VANTIX_FILE_1717460486104666006__'
{
  "images" : [
    {
      "idiom" : "universal",
      "platform" : "ios",
      "size" : "1024x1024"
    }
  ],
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}
__VANTIX_FILE_1717460486104666006__

mkdir -p "$ROOT/VANTIX/Resources/Assets.xcassets"
cat > "$ROOT/VANTIX/Resources/Assets.xcassets/Contents.json" <<'__VANTIX_FILE_5780027532811880646__'
{
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}
__VANTIX_FILE_5780027532811880646__

mkdir -p "$ROOT/VANTIX/Resources"
cat > "$ROOT/VANTIX/Resources/Info.plist" <<'__VANTIX_FILE_4899271733791935841__'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>VANTIX</string>
    <key>CFBundleName</key>
    <string>VANTIX</string>
    <key>CFBundleIdentifier</key>
    <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>CFBundleShortVersionString</key>
    <string>0.1.0</string>
    <key>UILaunchScreen</key>
    <dict/>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
    </array>
</dict>
</plist>
__VANTIX_FILE_4899271733791935841__

mkdir -p "$ROOT/."
cat > "$ROOT/project.yml" <<'__VANTIX_FILE_2996325014104325766__'
name: VANTIX

options:
  bundleIdPrefix: ai.vantix
  deploymentTarget:
    iOS: "17.0"
  createIntermediateGroups: true

settings:
  base:
    SWIFT_VERSION: "5.10"
    IPHONEOS_DEPLOYMENT_TARGET: "17.0"
    PRODUCT_BUNDLE_IDENTIFIER: ai.vantix.app
    TARGETED_DEVICE_FAMILY: "1"

targets:
  VANTIX:
    type: application
    platform: iOS
    sources:
      - path: VANTIX
    settings:
      base:
        INFOPLIST_FILE: VANTIX/Resources/Info.plist
        GENERATE_INFOPLIST_FILE: NO
        ASSETCATALOG_COMPILER_APPICON_NAME: AppIcon
    scheme:
      testTargets: []
__VANTIX_FILE_2996325014104325766__

mkdir -p "$ROOT/."
cat > "$ROOT/setup.sh" <<'__VANTIX_FILE_8000364667863638806__'
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
__VANTIX_FILE_8000364667863638806__

chmod +x "$ROOT/setup.sh" 2>/dev/null || true
echo "VANTIX structure created at: $ROOT"