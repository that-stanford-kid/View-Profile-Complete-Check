import SwiftUI

struct AlertsPlaceholderView: View {
    var body: some View {
        ZStack {
            VantixColors.graphite.ignoresSafeArea()

            VStack(spacing: 14) {
                Image(systemName: "bell.fill")
                    .font(.system(size: 28, weight: .semibold))
                    .foregroundStyle(VantixColors.cyan)

                Text("ALERTS")
                    .font(VantixTypography.title)
                    .foregroundStyle(VantixColors.primaryText)

                Text("Alert triage, anomaly workflows, and geofence triggers will be added after temporal intelligence.")
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
