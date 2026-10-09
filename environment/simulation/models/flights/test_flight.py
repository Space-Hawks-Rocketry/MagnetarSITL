
from rocketpy import Flight
from ..rockets.vehicle import rocket
from ..environments.env import env

test_flight = Flight(
    rocket=rocket,
    environment=env,
    rail_length=5.2,
    inclination=85,
    heading=0,
)