import Foundation
import Combine

@MainActor
final class IntelRepository: ObservableObject, IntelRepositoryProtocol {
    @Published private(set) var states: [ObjectState] = []

    private let services: [any IntelDomainService]
    private var objectsByID: [UUID: IntelObject] = [:]
    private var observationsByObjectID: [UUID: [Observation]] = [:]
    private var sourcesByID: [UUID: SourceRecord] = [:]

    init(services: [any IntelDomainService]) {
        self.services = services
    }

    var objectCount: Int { objectsByID.count }

    func load() async {
        var loadedObjects: [IntelObject] = []
        var loadedObservations: [Observation] = []

        for service in services {
            let objects = await service.fetchObjects()
            loadedObjects.append(contentsOf: objects)
            loadedObservations.append(contentsOf: await service.fetchInitialObservations(for: objects))

            for source in service.sourceRecords() {
                sourcesByID[source.id] = source
            }
        }

        objectsByID = Dictionary(uniqueKeysWithValues: loadedObjects.map { ($0.id, $0) })

        for observation in loadedObservations {
            observationsByObjectID[observation.objectID, default: []].append(observation)
        }

        rebuildStates()
    }

    func objectState(id: UUID) -> ObjectState? {
        states.first { $0.id == id }
    }

    func observations(for objectID: UUID) -> [Observation] {
        observationsByObjectID[objectID] ?? []
    }

    func append(_ observation: Observation) {
        observationsByObjectID[observation.objectID, default: []].append(observation)
        rebuildState(for: observation.objectID)
    }

    func source(id: UUID) -> SourceRecord? {
        sourcesByID[id]
    }

    private func rebuildStates() {
        states = objectsByID.values.compactMap { object in
            guard let observation = observationsByObjectID[object.id]?.max(by: { $0.timestamp < $1.timestamp }) else {
                return nil
            }

            return ObjectState(
                object: object,
                observation: observation,
                source: sourcesByID[observation.sourceID],
                severity: defaultSeverity(for: object)
            )
        }
        .sorted { $0.object.name < $1.object.name }
    }

    private func rebuildState(for objectID: UUID) {
        guard
            let object = objectsByID[objectID],
            let observation = observationsByObjectID[objectID]?.max(by: { $0.timestamp < $1.timestamp })
        else { return }

        let newState = ObjectState(
            object: object,
            observation: observation,
            source: sourcesByID[observation.sourceID],
            severity: defaultSeverity(for: object)
        )

        if let index = states.firstIndex(where: { $0.id == objectID }) {
            states[index] = newState
        } else {
            states.append(newState)
        }
    }

    private func defaultSeverity(for object: IntelObject) -> SeverityLevel {
        switch object.type {
        case .alert: .high
        case .event: .medium
        default: .informational
        }
    }
}
