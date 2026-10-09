
from rocketpy import Rocket
from motors.l1090w import l1090w
from sensors.sensors import *       # need to change name of sensors.py


# Geometry sized (see module docstring) so the dry CP-CG separation is 0.20 m.
# Coordinate origin = dry (no-motor) center of mass, "tail_to_nose" orientation.
BODY_RADIUS = 0.0508       # m (4 in airframe)
TOTAL_LENGTH = 2.88        # m

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

for sensor in [
    bmi323_accel, bmi323_gyro,
    lsm6dso32_accel, lsm6dso32_gyro,
    adxl375_accel,
    bmp581_baro, bmp390_baro,
    rm3100_mag, bmm150_mag,
    max_f10s_gnss
]:
    rocket.add_sensor(sensor, AV_BAY_POSITION)
