import Foundation

protocol IntelDomainService: Sendable {
    var domain: IntelDomain { get }
    func fetchObjects() async -> [IntelObject]
    func fetchInitialObservations(for objects: [IntelObject]) async -> [Observation]
    func sourceRecords() -> [SourceRecord]
}
