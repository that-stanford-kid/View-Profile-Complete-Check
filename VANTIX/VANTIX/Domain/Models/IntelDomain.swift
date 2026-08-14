import Foundation

enum IntelDomain: String, Codable, CaseIterable, Sendable {
    case air
    case land
    case sea
    case subsurface
    case space
    case rf
    case cyber
    case environment
}
