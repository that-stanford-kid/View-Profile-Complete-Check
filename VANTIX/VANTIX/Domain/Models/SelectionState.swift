import Foundation

struct SelectionState: Equatable {
    var selectedObjectID: UUID?
    var focusedObjectID: UUID?
    var inspectorPresentationState: InspectorPresentationState = .collapsed
}

enum InspectorPresentationState: Equatable {
    case collapsed
    case medium
    case expanded
}
