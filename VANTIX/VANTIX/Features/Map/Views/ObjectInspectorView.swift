import SwiftUI

struct ObjectInspectorView: View {
    let state: ObjectState

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Capsule()
                    .fill(VantixColors.tertiaryText)
                    .frame(width: 34, height: 4)
                    .frame(maxWidth: .infinity)

                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(state.object.name)
                            .font(VantixTypography.title)
                            .foregroundStyle(VantixColors.primaryText)

                        HStack(spacing: 7) {
                            Text(state.object.type.rawValue.uppercased())
                            Text("•")
                            Text(state.object.domain.rawValue.uppercased())
                        }
                        .font(VantixTypography.micro)
                        .foregroundStyle(VantixColors.secondaryText)
                    }

                    Spacer()

                    ConfidenceBadge(level: state.confidence)
                }

                Divider().overlay(VantixColors.border)

                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                    TelemetryCell(label: "STATUS", value: state.object.status.rawValue.uppercased())
                    TelemetryCell(label: "LAST UPDATE", value: state.timestamp.formatted(date: .omitted, time: .standard))
                    TelemetryCell(label: "LATITUDE", value: String(format: "%.4f°", state.coordinate.latitude))
                    TelemetryCell(label: "LONGITUDE", value: String(format: "%.4f°", state.coordinate.longitude))
                    TelemetryCell(label: "ALTITUDE", value: state.altitude.map { String(format: "%.0f ft", $0) } ?? "—")
                    TelemetryCell(label: "SPEED", value: state.speed.map { String(format: "%.0f kts", $0) } ?? "—")
                    TelemetryCell(label: "HEADING", value: state.heading.map { String(format: "%.0f°", $0) } ?? "—")
                    TelemetryCell(label: "SOURCE", value: state.source?.sourceType ?? "SIM")
                }

                HStack(spacing: 8) {
                    ActionButton(title: "TRACK", icon: "point.topleft.down.to.point.bottomright.curvepath")
                    ActionButton(title: "RELATIONSHIPS", icon: "point.3.connected.trianglepath.dotted")
                    ActionButton(title: "ANALYZE", icon: "sparkles")
                }

                Text("SIMULATED DATA")
                    .font(VantixTypography.micro)
                    .foregroundStyle(VantixColors.tertiaryText)
                    .frame(maxWidth: .infinity)
                    .padding(.top, 4)
            }
            .padding(16)
        }
        .background(VantixColors.graphite)
    }
}

private struct TelemetryCell: View {
    let label: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(label)
                .font(VantixTypography.micro)
                .foregroundStyle(VantixColors.tertiaryText)
            Text(value)
                .font(VantixTypography.telemetry)
                .foregroundStyle(VantixColors.primaryText)
                .lineLimit(1)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

private struct ConfidenceBadge: View {
    let level: ConfidenceLevel

    var body: some View {
        Text(level.rawValue.uppercased())
            .font(VantixTypography.micro)
            .foregroundStyle(level.color)
            .padding(.horizontal, 8)
            .padding(.vertical, 5)
            .background(level.color.opacity(0.10))
            .overlay {
                RoundedRectangle(cornerRadius: 6)
                    .stroke(level.color.opacity(0.45), lineWidth: 1)
            }
    }
}

private struct ActionButton: View {
    let title: String
    let icon: String

    var body: some View {
        Button {} label: {
            VStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.system(size: 13, weight: .semibold))
                Text(title)
                    .font(.system(size: 7, weight: .bold, design: .monospaced))
            }
            .foregroundStyle(VantixColors.cyan)
            .frame(maxWidth: .infinity)
            .frame(height: 54)
            .background(VantixColors.panel)
            .overlay {
                RoundedRectangle(cornerRadius: VantixRadius.control)
                    .stroke(VantixColors.border, lineWidth: 1)
            }
        }
        .buttonStyle(.plain)
    }
}
