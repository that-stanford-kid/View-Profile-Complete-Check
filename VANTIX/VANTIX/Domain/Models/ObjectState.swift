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
