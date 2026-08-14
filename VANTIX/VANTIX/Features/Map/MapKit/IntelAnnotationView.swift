import UIKit
import MapKit

final class IntelAnnotationView: MKAnnotationView {
    static let reuseIdentifier = "IntelAnnotationView"

    private let container = UIView()
    private let iconView = UIImageView()

    override init(annotation: MKAnnotation?, reuseIdentifier: String?) {
        super.init(annotation: annotation, reuseIdentifier: reuseIdentifier)
        collisionMode = .circle
        displayPriority = .defaultHigh
        clusteringIdentifier = "vantix.intel"
        centerOffset = CGPoint(x: 0, y: 0)

        container.translatesAutoresizingMaskIntoConstraints = false
        iconView.translatesAutoresizingMaskIntoConstraints = false

        addSubview(container)
        container.addSubview(iconView)

        NSLayoutConstraint.activate([
            container.widthAnchor.constraint(equalToConstant: 30),
            container.heightAnchor.constraint(equalToConstant: 30),
            container.centerXAnchor.constraint(equalTo: centerXAnchor),
            container.centerYAnchor.constraint(equalTo: centerYAnchor),

            iconView.widthAnchor.constraint(equalToConstant: 18),
            iconView.heightAnchor.constraint(equalToConstant: 18),
            iconView.centerXAnchor.constraint(equalTo: container.centerXAnchor),
            iconView.centerYAnchor.constraint(equalTo: container.centerYAnchor)
        ])

        frame = CGRect(x: 0, y: 0, width: 30, height: 30)
        container.layer.cornerRadius = 7
        container.layer.borderWidth = 1
        container.backgroundColor = UIColor(red: 0.02, green: 0.05, blue: 0.07, alpha: 0.90)
        iconView.contentMode = .scaleAspectFit
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override var annotation: MKAnnotation? {
        didSet { configure() }
    }

    func configure() {
        guard let intel = annotation as? IntelAnnotation else { return }

        iconView.image = UIImage(systemName: symbol(for: intel.type))?.withRenderingMode(.alwaysTemplate)
        iconView.tintColor = color(for: intel)
        container.layer.borderColor = color(for: intel).withAlphaComponent(0.55).cgColor

        if intel.type == .aircraft || intel.type == .vessel {
            iconView.transform = CGAffineTransform(rotationAngle: intel.heading * .pi / 180)
        } else {
            iconView.transform = .identity
        }
    }

    private func symbol(for type: IntelObjectType) -> String {
        switch type {
        case .aircraft: "airplane"
        case .vessel: "ferry.fill"
        case .satellite: "antenna.radiowaves.left.and.right"
        case .facility: "building.2.fill"
        case .event: "exclamationmark.triangle.fill"
        case .alert: "diamond.fill"
        case .buoy: "water.waves"
        case .tower: "dot.radiowaves.left.and.right"
        case .sensor: "sensor.fill"
        }
    }

    private func color(for annotation: IntelAnnotation) -> UIColor {
        switch annotation.severity {
        case .critical, .high:
            UIColor(red: 0.95, green: 0.26, blue: 0.30, alpha: 1)
        case .medium:
            UIColor(red: 1.00, green: 0.66, blue: 0.18, alpha: 1)
        case .low, .informational:
            switch annotation.domain {
            case .air, .space: UIColor(red: 0.20, green: 0.88, blue: 1.00, alpha: 1)
            case .sea, .subsurface: UIColor(red: 0.15, green: 0.78, blue: 0.72, alpha: 1)
            default: UIColor(red: 0.55, green: 0.80, blue: 0.92, alpha: 1)
            }
        }
    }
}
