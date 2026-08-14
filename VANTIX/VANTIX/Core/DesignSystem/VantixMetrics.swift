import SwiftUI

enum VantixSpacing {
    static let xxs: CGFloat = 4
    static let xs: CGFloat = 6
    static let sm: CGFloat = 8
    static let md: CGFloat = 12
    static let lg: CGFloat = 16
    static let xl: CGFloat = 24
}

enum VantixRadius {
    static let control: CGFloat = 8
    static let panel: CGFloat = 10
}

enum VantixTypography {
    static let micro = Font.system(size: 9, weight: .semibold, design: .monospaced)
    static let caption = Font.system(size: 11, weight: .medium, design: .default)
    static let telemetry = Font.system(size: 12, weight: .medium, design: .monospaced)
    static let body = Font.system(size: 14, weight: .medium)
    static let title = Font.system(size: 20, weight: .bold)
}
