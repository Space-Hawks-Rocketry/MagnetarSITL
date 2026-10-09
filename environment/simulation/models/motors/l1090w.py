
from rocketpy import SolidMotor

# Hand-built thrust curve matching published stats (see module docstring):
# total impulse 2671 Ns, burn time 2.5 s, avg thrust 1090 N, max thrust 1487 N.
L1090W_THRUST_CURVE = [
    (0.00, 1236.2),
    (0.04, 1420.0),
    (0.10, 1487.0),
    (0.20, 1445.0),
    (0.40, 1360.0),
    (0.70, 1265.0),
    (1.00, 1190.0),
    (1.30, 1115.0),
    (1.60, 1035.0),
    (1.90, 935.0),
    (2.10, 825.0),
    (2.30, 620.0),
    (2.45, 230.0),
    (2.50, 0.0),
]

l1090w = SolidMotor(
    thrust_source=L1090W_THRUST_CURVE,
    dry_mass=1.032,  # kg, 2.432 kg total - 1.400 kg propellant (per ThrustCurve.org)
    dry_inertia=(0.0075, 0.0075, 0.0006),  # rough estimate for a 54 mm x 626 mm case
    center_of_dry_mass_position=0.313,  # m from nozzle, roughly mid-case
    grains_center_of_mass_position=0.397,
    burn_time=2.5,
    grain_number=1,
    grain_separation=0.0,
    grain_density=1750,  # kg/m^3, typical APCP
    grain_outer_radius=0.0221,  # sized (with height/core below) so grain mass = 1.400 kg propellant
    grain_initial_inner_radius=0.008,
    grain_initial_height=0.60,
    nozzle_radius=0.022,
    throat_radius=0.010,
    interpolation_method="linear",
    nozzle_position=0,
    coordinate_system_orientation="nozzle_to_combustion_chamber",
)