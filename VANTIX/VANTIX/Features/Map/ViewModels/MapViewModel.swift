import Foundation
import Combine

@MainActor
final class MapViewModel: ObservableObject {
    @Published var recenterToken = 0
    @Published var showLayers = false
    @Published var showTimeline = false
    @Published var showAI = false
    @Published var searchText = ""

    func recenter() {
        recenterToken += 1
    }
}
