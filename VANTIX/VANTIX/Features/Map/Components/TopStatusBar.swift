import SwiftUI

struct TopStatusBar: View {
    @Binding var searchText: String

    var body: some View {
        VStack(spacing: 8) {
            HStack(spacing: 8) {
                HStack(spacing: 7) {
                    Image(systemName: "triangle.fill")
                        .font(.system(size: 12))
                        .foregroundStyle(VantixColors.cyan)
                    Text("VANTIX")
                        .font(.system(size: 17, weight: .black, design: .rounded))
                        .foregroundStyle(VantixColors.primaryText)
                }

                HStack(spacing: 6) {
                    Image(systemName: "magnifyingglass")
                        .foregroundStyle(VantixColors.secondaryText)
                    TextField("Search assets, IDs…", text: $searchText)
                        .font(VantixTypography.caption)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                }
                .padding(.horizontal, 10)
                .frame(height: 34)
                .background(VantixColors.panel.opacity(0.93))
                .overlay {
                    RoundedRectangle(cornerRadius: VantixRadius.control)
                        .stroke(VantixColors.border, lineWidth: 1)
                }
            }

            HStack(spacing: 0) {
                StatusCell(label: "SITUATION", value: "ELEVATED", valueColor: VantixColors.amber)
                Divider().overlay(VantixColors.border)
                StatusCell(label: "OBJECTS", value: "122", valueColor: VantixColors.cyan)
                Divider().overlay(VantixColors.border)
                StatusCell(label: "SYSTEM", value: "OPERATIONAL", valueColor: VantixColors.success)
            }
            .frame(height: 42)
            .background(VantixColors.panel.opacity(0.92))
            .overlay {
                RoundedRectangle(cornerRadius: VantixRadius.control)
                    .stroke(VantixColors.border, lineWidth: 1)
            }
        }
        .padding(.horizontal, 10)
    }
}

private struct StatusCell: View {
    let label: String
    let value: String
    let valueColor: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label)
                .font(VantixTypography.micro)
                .foregroundStyle(VantixColors.tertiaryText)
            Text(value)
                .font(.system(size: 10, weight: .bold, design: .monospaced))
                .foregroundStyle(valueColor)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 8)
    }
}
