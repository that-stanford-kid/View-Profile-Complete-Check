import SwiftUI

struct MorePlaceholderView: View {
    var body: some View {
        ZStack {
            VantixColors.graphite.ignoresSafeArea()

            VStack(spacing: 14) {
                Image(systemName: "ellipsis")
                    .font(.system(size: 28, weight: .semibold))
                    .foregroundStyle(VantixColors.cyan)

                Text("MORE")
                    .font(VantixTypography.title)
                    .foregroundStyle(VantixColors.primaryText)

                Text("Settings, data sources, permissions, diagnostics, and enterprise controls.")
                    .font(VantixTypography.body)
                    .foregroundStyle(VantixColors.secondaryText)
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: 310)

                Text("SIMULATED DATA")
                    .font(VantixTypography.micro)
                    .foregroundStyle(VantixColors.tertiaryText)
                    .padding(.top, 8)
            }
        }
    }
}
