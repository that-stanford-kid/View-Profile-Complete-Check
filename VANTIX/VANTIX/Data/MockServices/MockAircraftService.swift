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
