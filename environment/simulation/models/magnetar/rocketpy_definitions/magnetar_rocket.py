from rocketpy import Rocket

from .L1090W_motor import l1090w
from .sensors.accelerometers import *
from .sensors.gyroscopes import *
from .sensors.barometers import *
from .sensors.magnetometers import *
from .sensors.gnss_receivers import *

# Geometry sized (see module docstring) so the dry CP-CG separation is 0.20 m.
# Coordinate origin = dry (no-motor) center of mass, "tail_to_nose" orientation.
BODY_RADIUS = 0.0508       # m (4 in airframe)
TOTAL_LENGTH = 2.88        # m
AV_BAY_POSITION = 0.3      # Distance of dry bay from CG

rocket = Rocket(
    radius=BODY_RADIUS,
    mass=11.2,  # kg, dry, no motor
    inertia=(7.5, 7.5, 0.025),  # kg*m^2, engineering estimate (Iyy=Ixx, Iroll)
    power_off_drag=0.393,
    power_on_drag=0.393,
    center_of_mass_without_motor=0,  # origin IS the dry CG
    coordinate_system_orientation="tail_to_nose",
)

rocket.add_motor(l1090w, position=-0.709)  # nozzle position, at the very tail

nose = rocket.add_nose(length=0.50, kind="von karman", position=2.171)

fins = rocket.add_trapezoidal_fins(
    n=4,
    root_chord=0.18,
    tip_chord=0.09,
    span=0.11,
    sweep_length=0.12,
    position=-0.509,  # fin root leading edge
    cant_angle=0,
)

rail_buttons = rocket.set_rail_buttons(
    upper_button_position=1.2,
    lower_button_position=-0.4,
    angular_position=45,
)

sensors = [
    bmi323_accel, lsm6dso32_accel, adxl375_accel, truth_accel,
    bmi323_gyro, lsm6dso32_gyro, truth_gyro,
    bmp581_baro, bmp390_baro, truth_baro,
    rm3100_mag, bmm150_mag, truth_mag,
    max_f10s_gnss, truth_gnss
]

for sensor in sensors:
    rocket.add_sensor(sensor, AV_BAY_POSITION)
    

