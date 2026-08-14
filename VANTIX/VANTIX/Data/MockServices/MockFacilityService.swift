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
