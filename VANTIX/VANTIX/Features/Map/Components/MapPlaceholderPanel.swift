import SwiftUI

struct MapPlaceholderPanel: View {
    let title: String
    let bodyText: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(VantixTypography.caption)
                .foregroundStyle(VantixColors.cyan)
            Text(bodyText)
                .font(VantixTypography.caption)
                .foregroundStyle(VantixColors.secondaryText)
        }
        .padding(12)
        .frame(maxWidth: 260, alignment: .leading)
        .background(VantixColors.panel.opacity(0.97))
        .overlay {
            RoundedRectangle(cornerRadius: VantixRadius.panel)
                .stroke(VantixColors.border, lineWidth: 1)
        }
    }
}
