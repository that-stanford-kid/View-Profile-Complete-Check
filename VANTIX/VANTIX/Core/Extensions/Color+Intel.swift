import SwiftUI

extension SeverityLevel {
    var color: Color {
        switch self {
        case .critical, .high: VantixColors.critical
        case .medium: VantixColors.amber
        case .low: VantixColors.cyan
        case .informational: VantixColors.teal
        }
    }
}

extension ConfidenceLevel {
    var color: Color {
        switch self {
        case .confirmed, .high: VantixColors.success
        case .medium: VantixColors.amber
        case .low, .unverified: VantixColors.secondaryText
        }
    }
}
