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
