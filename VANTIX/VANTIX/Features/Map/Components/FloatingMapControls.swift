import SwiftUI

struct FloatingMapControls: View {
    let onLayers: () -> Void
    let onTimeline: () -> Void
    let onAI: () -> Void
    let onRecenter: () -> Void

    var body: some View {
        VStack(spacing: 7) {
            ControlButton(icon: "square.3.layers.3d", label: "LAYERS", action: onLayers)
            ControlButton(icon: "clock.arrow.circlepath", label: "TIME", action: onTimeline)
            ControlButton(icon: "sparkles", label: "AI", tint: .purple, action: onAI)
            ControlButton(icon: "scope", label: "CENTER", action: onRecenter)
        }
    }
}

private struct ControlButton: View {
    let icon: String
    let label: String
    var tint: Color = VantixColors.cyan
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 3) {
                Image(systemName: icon)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundStyle(tint)
                Text(label)
                    .font(.system(size: 7, weight: .bold, design: .monospaced))
                    .foregroundStyle(VantixColors.secondaryText)
            }
            .frame(width: 52, height: 48)
            .background(VantixColors.panel.opacity(0.94))
            .overlay {
                RoundedRectangle(cornerRadius: VantixRadius.control)
                    .stroke(VantixColors.border, lineWidth: 1)
            }
        }
        .buttonStyle(.plain)
    }
}
