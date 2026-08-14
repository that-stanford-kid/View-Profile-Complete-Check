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
