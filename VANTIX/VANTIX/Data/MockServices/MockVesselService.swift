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
