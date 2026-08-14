import Foundation
import CoreLocation

enum IntelObjectType: String, Codable, CaseIterable, Sendable {
    case aircraft
    case vessel
    case satellite
    case facility
    case event
    case alert
    case buoy
    case tower
    case sensor
}

enum IntelStatus: String, Codable, Sendable {
    case active
    case inTransit
    case stationary
    case degraded
    case offline
    case unknown
}

struct IntelObject: Identifiable, Codable, Hashable, Sendable {
    let id: UUID
    let type: IntelObjectType
    let domain: IntelDomain
    var name: String
    var callsign: String?
    var description: String?
    var status: IntelStatus
    var tags: [String]
    var metadata: [String: String]
    var createdAt: Date
    var updatedAt: Date
}
