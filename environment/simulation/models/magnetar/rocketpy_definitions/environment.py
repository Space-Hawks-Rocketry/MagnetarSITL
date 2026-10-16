from datetime import datetime
from rocketpy import Environment

LAUNCH_LAT = 29.232838813115663
LAUNCH_LON = -95.12175043164375
LAUNCH_ELEVATION = 10.0  # m ASL, rough value for this part of the Texas coastal plain

# launch_date = datetime(2026, 10, 15, 15, 0, 0, tzinfo=timezone.utc)  # adjust as needed
launch_date = datetime(2026, 10, 15, 15, 0, 0)  # adjust as needed

env = Environment(
    latitude=LAUNCH_LAT,
    longitude=LAUNCH_LON,
    elevation=LAUNCH_ELEVATION,
)
env.set_date(launch_date, timezone="UTC")
env.set_atmospheric_model(type="standard_atmosphere")  # swap for "Forecast"/"Reanalysis" if desired

# NOTE: This one gives 0 below 100m (NOT GOOD)
# env.set_atmospheric_model(type="forecast", file="GFS")  # swap for "Forecast"/"Reanalysis" if desired