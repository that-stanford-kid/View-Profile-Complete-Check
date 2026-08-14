import Foundation

enum SourceReliability: String, Codable, Sendable {
    case confirmed
    case high
    case medium
    case low
    case unknown
}

enum SourceStatus: String, Codable, Sendable {
    case online
    case degraded
    case delayed
    case offline
    case simulated
}

struct SourceRecord: Identifiable, Codable, Hashable, Sendable {
    let id: UUID
    let name: String
    let sourceType: String
    let domain: IntelDomain
    let reliability: SourceReliability
    let status: SourceStatus
    let lastUpdated: Date
}
