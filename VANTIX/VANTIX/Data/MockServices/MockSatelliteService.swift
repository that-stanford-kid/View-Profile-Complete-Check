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
