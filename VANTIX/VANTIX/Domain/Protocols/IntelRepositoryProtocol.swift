import Foundation

@MainActor
protocol IntelRepositoryProtocol: AnyObject {
    var states: [ObjectState] { get }
    var objectCount: Int { get }

    func load() async
    func objectState(id: UUID) -> ObjectState?
    func append(_ observation: Observation)
    func observations(for objectID: UUID) -> [Observation]
}
