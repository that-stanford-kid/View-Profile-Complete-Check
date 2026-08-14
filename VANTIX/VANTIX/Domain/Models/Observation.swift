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
