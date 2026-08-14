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
