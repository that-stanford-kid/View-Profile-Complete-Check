import SwiftUI

struct IntelPlaceholderView: View {
    var body: some View {
        ZStack {
            VantixColors.graphite.ignoresSafeArea()

            VStack(spacing: 14) {
                Image(systemName: "waveform.path.ecg.rectangle")
                    .font(.system(size: 28, weight: .semibold))
                    .foregroundStyle(VantixColors.cyan)

                Text("INTEL")
                    .font(VantixTypography.title)
                    .foregroundStyle(VantixColors.primaryText)

                Text("Situations, event feeds, source health, and sensor intelligence arrive in Prompt 3.")
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
