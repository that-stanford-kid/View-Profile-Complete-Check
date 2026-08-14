import Foundation

@MainActor
final class SimulationEngine {
    private weak var repository: IntelRepository?
    private var task: Task<Void, Never>?

    init(repository: IntelRepository) {
        self.repository = repository
    }

    func start() {
        guard task == nil else { return }

        task = Task { [weak self] in
            while !Task.isCancelled {
                try? await Task.sleep(for: .milliseconds(900))
                guard let self, let repository = self.repository else { continue }

                let moving = repository.states
                    .filter { $0.object.type == .aircraft || $0.object.type == .vessel }
                    .prefix(24)

                for state in moving {
                    let heading = state.heading ?? 0
                    let speed = state.speed ?? 0
                    let distanceDegrees = max(speed, 1) / 90000.0

                    let radians = heading * .pi / 180
                    let nextLat = state.coordinate.latitude + cos(radians) * distanceDegrees
                    let nextLon = state.coordinate.longitude + sin(radians) * distanceDegrees

                    let observation = Observation(
                        id: UUID(),
                        objectID: state.id,
                        timestamp: .now,
                        latitude: nextLat,
                        longitude: nextLon,
                        altitude: state.altitude,
                        depth: state.depth,
                        speed: speed + Double.random(in: -2...2),
                        heading: (heading + Double.random(in: -1.5...1.5)).truncatingRemainder(dividingBy: 360),
                        value: nil,
                        sourceID: state.observation.sourceID,
                        confidence: state.confidence,
                        metadata: ["simulated": "true"]
                    )

                    repository.append(observation)
                }
            }
        }
    }

    func stop() {
        task?.cancel()
        task = nil
    }

    deinit {
        task?.cancel()
    }
}
