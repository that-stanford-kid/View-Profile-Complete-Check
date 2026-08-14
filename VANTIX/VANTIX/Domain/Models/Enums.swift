import Foundation

enum ConfidenceLevel: String, Codable, CaseIterable, Sendable {
    case confirmed
    case high
    case medium
    case low
    case unverified
}

enum SeverityLevel: String, Codable, CaseIterable, Sendable {
    case critical
    case high
    case medium
    case low
    case informational
}
