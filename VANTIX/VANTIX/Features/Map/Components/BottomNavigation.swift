import SwiftUI

struct BottomNavigation: View {
    @Binding var selectedTab: AppTab

    var body: some View {
        HStack(spacing: 0) {
            ForEach(AppTab.allCases) { tab in
                Button {
                    selectedTab = tab
                } label: {
                    VStack(spacing: 3) {
                        Image(systemName: tab.icon)
                            .font(.system(size: 15, weight: .semibold))
                        Text(tab.rawValue)
                            .font(.system(size: 8, weight: .bold, design: .monospaced))
                    }
                    .foregroundStyle(selectedTab == tab ? VantixColors.cyan : VantixColors.secondaryText)
                    .frame(maxWidth: .infinity)
                    .frame(height: 51)
                }
                .buttonStyle(.plain)
            }
        }
        .background(VantixColors.graphite.opacity(0.96))
        .overlay(alignment: .top) {
            Rectangle()
                .fill(VantixColors.border)
                .frame(height: 1)
        }
    }
}
