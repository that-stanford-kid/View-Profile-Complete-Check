import SwiftUI

struct MainMapView: View {
    @EnvironmentObject private var environment: AppEnvironment
    @StateObject private var viewModel = MapViewModel()

    private var selectedState: ObjectState? {
        guard let id = environment.selection.selectedObjectID else { return nil }
        return environment.repository.objectState(id: id)
    }

    var body: some View {
        ZStack {
            VantixMapView(
                states: filteredStates,
                selectedObjectID: Binding(
                    get: { environment.selection.selectedObjectID },
                    set: { newValue in
                        environment.selection.selectedObjectID = newValue
                        environment.selection.focusedObjectID = newValue
                    }
                ),
                focusObjectID: environment.selection.focusedObjectID,
                recenterToken: viewModel.recenterToken
            )
            .ignoresSafeArea()

            LinearGradient(
                colors: [VantixColors.graphite.opacity(0.62), .clear, VantixColors.graphite.opacity(0.38)],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()
            .allowsHitTesting(false)

            VStack {
                TopStatusBar(searchText: $viewModel.searchText)
                    .padding(.top, 4)

                Spacer()

                HStack {
                    Spacer()
                    FloatingMapControls(
                        onLayers: { viewModel.showLayers.toggle() },
                        onTimeline: { viewModel.showTimeline.toggle() },
                        onAI: { viewModel.showAI.toggle() },
                        onRecenter: { viewModel.recenter() }
                    )
                    .padding(.trailing, 10)
                    .padding(.bottom, 76)
                }
            }

            if viewModel.showLayers {
                VStack {
                    Spacer()
                    HStack {
                        MapPlaceholderPanel(
                            title: "LAYERS",
                            bodyText: "Prompt 1 foundation ready. Domain layers arrive in Prompt 3."
                        )
                        Spacer()
                    }
                    .padding(.leading, 10)
                    .padding(.bottom, 74)
                }
            }

            VStack {
                Spacer()
                Text("SIMULATED DATA")
                    .font(VantixTypography.micro)
                    .foregroundStyle(VantixColors.tertiaryText)
                    .padding(.bottom, 58)
            }
        }
        .sheet(item: Binding(
            get: { selectedState },
            set: { _ in
                environment.selection.selectedObjectID = nil
                environment.selection.focusedObjectID = nil
            }
        )) { state in
            ObjectInspectorView(state: state)
                .presentationDetents([.fraction(0.22), .medium, .large])
                .presentationDragIndicator(.hidden)
                .presentationBackground(VantixColors.graphite)
        }
    }

    private var filteredStates: [ObjectState] {
        let query = viewModel.searchText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !query.isEmpty else { return environment.repository.states }

        return environment.repository.states.filter {
            $0.object.name.localizedCaseInsensitiveContains(query) ||
            ($0.object.callsign?.localizedCaseInsensitiveContains(query) ?? false) ||
            $0.object.type.rawValue.localizedCaseInsensitiveContains(query)
        }
    }
}
