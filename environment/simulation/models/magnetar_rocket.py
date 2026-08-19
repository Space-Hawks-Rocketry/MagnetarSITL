from rocketpy import Environment, SolidMotor, Rocket, Flight
import datetime

LAUNCH_DATE = datetime.date.today()
LAUNCH_LATITUDE = 29.76    # decimal degrees
LAUNCH_LONGITUDE = 95.37   # decimal degrees
LAUNCH_ELEVATION = 11.0    # m
# https://en.wikipedia.org/wiki/List_of_moments_of_inertia
ROCKET_MOTOR = SolidMotor(
    thrust_source="./environment/simulation/models/resources/AeroTech_L1090W.eng",
    dry_mass=1.032,
    dry_inertia=(0.138, 0.0138, 0.000316),
    nozzle_radius=5.78 / 1000, # Comes from Gemini lol, check this
    grain_number=6,
    grain_density=1815,
    grain_outer_radius=33 / 1000,
    grain_initial_inner_radius=15 / 1000,
    grain_initial_height=120 / 1000,
    grain_separation=5 / 1000,
    grains_center_of_mass_position=0.397,
    center_of_dry_mass_position=0.317,
    nozzle_position=0,
    burn_time=3.9,
    throat_radius=11 / 1000,
    coordinate_system_orientation="nozzle_to_combustion_chamber",
)

## https://docs.rocketpy.org/en/latest/user/first_simulation.html#setting-up-a-simulation
class MagnetarRocket:

    def __init__(self):
        env = Environment(latitude=LAUNCH_LATITUDE, longitude=LAUNCH_LONGITUDE, elevation=LAUNCH_ELEVATION)
        env.set_date((LAUNCH_DATE.year, LAUNCH_DATE.month, LAUNCH_DATE.day, 12))
        env.set_atmospheric_model(type="Forecast", file="GFS")
        
        ROCKET_MOTOR.info()
        
        