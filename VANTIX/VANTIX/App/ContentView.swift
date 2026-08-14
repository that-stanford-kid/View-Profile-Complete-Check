import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var environment: AppEnvironment

    var body: some View {
        ZStack(alignment: .bottom) {
            Group {
                switch environment.selectedTab {
                case .map:
                    MainMapView()
                case .intel:
                    IntelPlaceholderView()
                case .graph:
                    GraphPlaceholderView()
                case .alerts:
                    AlertsPlaceholderView()
                case .more:
                    MorePlaceholderView()
                }
            }

            BottomNavigation(selectedTab: $environment.selectedTab)
        }
        .ignoresSafeArea(edges: .bottom)
        .task {
            await environment.bootstrap()
        }
    }
}
