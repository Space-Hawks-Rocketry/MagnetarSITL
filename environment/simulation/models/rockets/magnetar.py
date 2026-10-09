

from rocketpy import Flight
from . import vehicle
from ..environments.env import env
from ..flights.test_flight import test_flight

from bisect import bisect_left

def _nearest_reading(sensor, t):
    """Return the (time, *values) row in sensor.measured_data closest to t."""
    data = sensor.measured_data
    if not data:
        return None
    times = [row[0] for row in data]
    idx = bisect_left(times, t)
    if idx == 0:
        return data[0]
    if idx == len(times):
        return data[-1]
    before, after = data[idx - 1], data[idx]
    return before if (t - before[0]) <= (after[0] - t) else after


class MagnetarRocket:

    def __init__(self, t0=0.0):
        self.t = t0
        self.test_flight = test_flight
        
    def update(self, t: float):
        self.t = t
        
    def measure(self):
        bmi323_a = _nearest_reading(vehicle.bmi323_accel, self.t)
        bmi323_g = _nearest_reading(vehicle.bmi323_gyro, self.t)
        lsm_a    = _nearest_reading(vehicle.lsm6dso32_accel, self.t)
        lsm_g    = _nearest_reading(vehicle.lsm6dso32_gyro, self.t)
        adxl_a   = _nearest_reading(vehicle.adxl375_accel, self.t)
        bmm_m    = _nearest_reading(vehicle.bmm150_mag, self.t)
        rm_m     = _nearest_reading(vehicle.rm3100_mag, self.t)
        bmp390_b = _nearest_reading(vehicle.bmp390_baro, self.t)
        bmp581_b = _nearest_reading(vehicle.bmp581_baro, self.t)
        max_gnss = _nearest_reading(vehicle.max_f10s_gnss, self.t)

        def vec3(row):
            if row is None:
                return {"x": None, "y": None, "z": None}
            _, x, y, z = row
            return {"x": x, "y": y, "z": z}

        def baro(row):
            if row is None:
                return {"baro": None}
            pressure = row[1]
            return {"baro": pressure}

        return {
            "timestamp": self.t,
            "gnss": {
                "pos": vec3(max_gnss)
            },

            "bmi323": {
                "accel": vec3(bmi323_a),
                "gyro": vec3(bmi323_g),
            },

            "lsm6dso32": {
                "accel": vec3(lsm_a),
                "gyro": vec3(lsm_g),
            },

            "adxl375": {
                "accel": vec3(adxl_a),
            },

            "bmm150": {
                "mag": vec3(bmm_m),
            },
            "rm": {
                "mag": vec3(rm_m),
            },

            "bmp390": baro(bmp390_b),

            "bmp581": baro(bmp581_b),

            "main_battery": None,
            "pyro": {
                "battery": None,
                "pyro_0_continuity": None,
                "pyro_0_status": None,
                "pyro_1_continuity": None,
                "pyro_1_status": None
            }
        }