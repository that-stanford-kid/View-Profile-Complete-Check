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
