import SwiftUI

struct GraphPlaceholderView: View {
    var body: some View {
        ZStack {
            VantixColors.graphite.ignoresSafeArea()

            VStack(spacing: 14) {
                Image(systemName: "point.3.connected.trianglepath.dotted")
                    .font(.system(size: 28, weight: .semibold))
                    .foregroundStyle(VantixColors.cyan)

                Text("GRAPH")
                    .font(VantixTypography.title)
                    .foregroundStyle(VantixColors.primaryText)

                Text("Entity relationships and correlation graph are staged for a later milestone.")
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
