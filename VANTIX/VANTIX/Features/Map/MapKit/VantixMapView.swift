import SwiftUI
import MapKit

struct VantixMapView: UIViewRepresentable {
    let states: [ObjectState]
    @Binding var selectedObjectID: UUID?
    let focusObjectID: UUID?
    let recenterToken: Int

    func makeCoordinator() -> Coordinator {
        Coordinator(parent: self)
    }

    func makeUIView(context: Context) -> MKMapView {
        let map = MKMapView(frame: .zero)
        map.delegate = context.coordinator
        map.overrideUserInterfaceStyle = .dark
        map.showsCompass = false
        map.showsScale = false
        map.pointOfInterestFilter = .excludingAll
        map.isRotateEnabled = true
        map.isPitchEnabled = true

        let configuration = MKStandardMapConfiguration(elevationStyle: .realistic)
        configuration.emphasisStyle = .muted
        map.preferredConfiguration = configuration

        map.register(
            IntelAnnotationView.self,
            forAnnotationViewWithReuseIdentifier: IntelAnnotationView.reuseIdentifier
        )
        map.register(
            MKMarkerAnnotationView.self,
            forAnnotationViewWithReuseIdentifier: MKMapViewDefaultClusterAnnotationViewReuseIdentifier
        )

        map.setCamera(defaultCamera(), animated: false)
        context.coordinator.sync(states, on: map)
        return map
    }

    func updateUIView(_ map: MKMapView, context: Context) {
        context.coordinator.parent = self
        context.coordinator.sync(states, on: map)

        if context.coordinator.lastRecenterToken != recenterToken {
            context.coordinator.lastRecenterToken = recenterToken
            map.setCamera(defaultCamera(), animated: true)
        }

        if let focusObjectID,
           context.coordinator.lastFocusedObjectID != focusObjectID,
           let annotation = context.coordinator.annotationsByID[focusObjectID] {
            context.coordinator.lastFocusedObjectID = focusObjectID
            map.setCenter(annotation.coordinate, animated: true)
            map.selectAnnotation(annotation, animated: true)
        }
    }

    private func defaultCamera() -> MKMapCamera {
        MKMapCamera(
            lookingAtCenter: CLLocationCoordinate2D(latitude: 34, longitude: 16),
            fromDistance: 11_000_000,
            pitch: 18,
            heading: 0
        )
    }

    final class Coordinator: NSObject, MKMapViewDelegate {
        var parent: VantixMapView
        var annotationsByID: [UUID: IntelAnnotation] = [:]
        var lastRecenterToken = 0
        var lastFocusedObjectID: UUID?

        init(parent: VantixMapView) {
            self.parent = parent
        }

        func sync(_ states: [ObjectState], on map: MKMapView) {
            let incomingIDs = Set(states.map(\.id))
            let stale = annotationsByID.filter { !incomingIDs.contains($0.key) }

            if !stale.isEmpty {
                map.removeAnnotations(Array(stale.values))
                for id in stale.keys { annotationsByID.removeValue(forKey: id) }
            }

            var additions: [IntelAnnotation] = []

            for state in states {
                if let annotation = annotationsByID[state.id] {
                    annotation.apply(state)
                    if let view = map.view(for: annotation) as? IntelAnnotationView {
                        view.configure()
                    }
                } else {
                    let annotation = IntelAnnotation(state: state)
                    annotationsByID[state.id] = annotation
                    additions.append(annotation)
                }
            }

            if !additions.isEmpty {
                map.addAnnotations(additions)
            }
        }

        func mapView(_ mapView: MKMapView, viewFor annotation: MKAnnotation) -> MKAnnotationView? {
            if let cluster = annotation as? MKClusterAnnotation {
                let view = mapView.dequeueReusableAnnotationView(
                    withIdentifier: MKMapViewDefaultClusterAnnotationViewReuseIdentifier,
                    for: cluster
                ) as! MKMarkerAnnotationView
                view.markerTintColor = UIColor(red: 0.08, green: 0.52, blue: 0.64, alpha: 0.92)
                view.glyphText = "\(cluster.memberAnnotations.count)"
                view.glyphTintColor = .white
                view.displayPriority = .defaultHigh
                return view
            }

            guard annotation is IntelAnnotation else { return nil }
            let view = mapView.dequeueReusableAnnotationView(
                withIdentifier: IntelAnnotationView.reuseIdentifier,
                for: annotation
            ) as! IntelAnnotationView
            view.configure()
            return view
        }

        func mapView(_ mapView: MKMapView, didSelect view: MKAnnotationView) {
            if let cluster = view.annotation as? MKClusterAnnotation {
                mapView.showAnnotations(cluster.memberAnnotations, animated: true)
                return
            }

            guard let annotation = view.annotation as? IntelAnnotation else { return }
            parent.selectedObjectID = annotation.objectID

            let camera = MKMapCamera(
                lookingAtCenter: annotation.coordinate,
                fromDistance: max(mapView.camera.centerCoordinateDistance * 0.65, 45_000),
                pitch: max(mapView.camera.pitch, 28),
                heading: mapView.camera.heading
            )
            mapView.setCamera(camera, animated: true)
        }
    }
}
