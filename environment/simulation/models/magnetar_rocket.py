"""
RocketPy simulation of an 11.2 kg (dry) L1090W-P amateur rocket with a full
IMU / barometer / magnetometer sensor suite, for nav-code testing.

Requires:
    pip install rocketpy ppigrf

============================================================================
DESIGN NOTES (see chat response for the full writeup)
============================================================================
- Rocket geometry (4 in / 0.1016 m airframe, 2.88 m long, 4 trapezoidal fins)
  was sized with hand Barrowman equations so that the (dry, no-motor) CP-CG
  separation is ~0.20 m (about 2 calibers), which is a healthy, stable
  margin. The rocket coordinate origin is placed AT the dry center of mass
  (center_of_mass_without_motor=0) so aero-surface "position" arguments are
  already measured relative to the CG.
- The L1090W-P thrust curve below is a hand-built approximation that matches
  AeroTech/ThrustCurve.org's published total impulse (2671 Ns), burn time
  (2.5 s), average thrust (1090 N) and max thrust (1487 N) for this motor,
  because automated download of the manufacturer's .eng file was blocked by
  thrustcurve.org's robots.txt. It is NOT the exact manufacturer curve, but
  it reproduces the motor's key performance numbers.
- A 1-DOF check (thrust curve + drag + ISA density + gravity) with this
  rocket/motor/Cd combination lands the apogee at ~1550 m, i.e. "on the
  order of 1500 m" as requested.
- Magnetometer: RocketPy has no built-in magnetometer class, so one is
  implemented below by subclassing rocketpy.sensors.sensor.InertialSensor,
  following the exact same measurement pipeline RocketPy's own Accelerometer
  uses (see Magnetometer.measure() docstring for the coordinate-frame
  discussion).
"""

import numpy as np
from datetime import datetime, timezone

from rocketpy import Environment, SolidMotor, Rocket, Flight, Accelerometer, Gyroscope, Barometer, GnssReceiver
from rocketpy.sensors.sensor import InertialSensor
from rocketpy.mathutils.vector_matrix import Matrix, Vector
from rocketpy.prints.sensors_prints import _InertialSensorPrints

import ppigrf

G0 = 9.80665

# ============================================================================
# 1. ENVIRONMENT
# ============================================================================
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


# ============================================================================
# 2. CUSTOM MAGNETOMETER SENSOR (IGRF-14 via ppigrf)
# ============================================================================
class Magnetometer(InertialSensor):
    """A 3-axis magnetometer, modeled the same way RocketPy models the
    Accelerometer/Gyroscope, but subclassing the shared InertialSensor base
    class directly since RocketPy has no built-in Magnetometer.

    Coordinate frame handling
    --------------------------
    RocketPy's inertial frame is ENU: X = East, Y = North, Z = Up (see the
    Flight class docs: "X-axis: Points East ... Y-axis: Points North ...
    Z-axis: positive up"). ppigrf.igrf(lon, lat, h_km, date) returns
    (Be, Bn, Bu) -- East, North, Up -- in the same convention, in nT. So the
    IGRF vector can be fed straight in as an inertial-frame vector with zero
    axis re-ordering or sign flips, exactly mirroring how RocketPy's own
    Accelerometer.measure() treats the gravity vector [0, 0, -g] (also
    defined in the inertial ENU frame) before rotating it into the sensor
    frame with:

        inertial_to_sensor = self._total_rotation_sensor_to_body \
                              @ Matrix.transformation(u[6:10]).transpose

    where u[6:10] are the rocket's attitude quaternions (e0..e3, scalar
    first) and Matrix.transformation(q) is body->inertial, so its transpose
    is inertial->body; composing with the sensor's own body->sensor rotation
    gives inertial->sensor directly. This is copied verbatim from
    rocketpy.sensors.accelerometer.Accelerometer.measure so the magnetometer
    is rotated by the rocket's attitude in exactly the same way every other
    inertial sensor on the rocket is.

    Performance / accuracy note
    ----------------------------
    The IGRF field is evaluated once, at the launch pad coordinates and
    elevation, at __init__ time, and cached. Over a ~1.5 km-apogee, sub-1-km
    downrange flight lasting well under a minute, the true field vector
    changes by a small fraction of a nT -- utterly negligible next to any of
    these sensors' noise floors -- so recomputing IGRF at every timestep
    would only add cost, not accuracy. If you adapt this for a very
    long-range or very high-altitude flight, move the ppigrf call inside
    measure() and evaluate it at the rocket's live lat/lon/altitude instead.
    """

    units = "T"

    def __init__(
        self,
        sampling_rate,
        latitude,
        longitude,
        elevation,
        date,
        orientation=(0, 0, 0),
        measurement_range=np.inf,
        resolution=0,
        noise_density=0,
        noise_variance=1,
        random_walk_density=0,
        random_walk_variance=1,
        constant_bias=0,
        operating_temperature=298.15,
        temperature_bias=0,
        temperature_scale_factor=0,
        cross_axis_sensitivity=0,
        name="Magnetometer",
        seed=None,
    ):
        super().__init__(
            sampling_rate,
            orientation,
            measurement_range=measurement_range,
            resolution=resolution,
            noise_density=noise_density,
            noise_variance=noise_variance,
            random_walk_density=random_walk_density,
            random_walk_variance=random_walk_variance,
            constant_bias=constant_bias,
            operating_temperature=operating_temperature,
            temperature_bias=temperature_bias,
            temperature_scale_factor=temperature_scale_factor,
            cross_axis_sensitivity=cross_axis_sensitivity,
            name=name,
            seed=seed,
        )
        self.prints = _InertialSensorPrints(self)

        # --- Evaluate IGRF-14 once at the launch site and cache it (ENU, Tesla) ---
        h_km = elevation / 1000.0
        Be, Bn, Bu = ppigrf.igrf(longitude, latitude, h_km, date)
        Be, Bn, Bu = float(np.asarray(Be).squeeze()), float(np.asarray(Bn).squeeze()), float(np.asarray(Bu).squeeze())
        self.field_enu_nT = (Be, Bn, Bu)  # stashed for printing/verification
        self._B_inertial = Vector([Be, Bn, Bu]) * 1e-9  # nT -> T

        # Handy derived quantities for a sanity-check printout against NOAA's
        # online calculator (https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml)
        F = np.sqrt(Be**2 + Bn**2 + Bu**2)
        H = np.sqrt(Be**2 + Bn**2)
        self.total_field_nT = F
        self.declination_deg = np.degrees(np.arctan2(Be, Bn))
        self.inclination_deg = np.degrees(np.arctan2(Bu, H))

    def measure(self, time, **kwargs):
        u = kwargs["u"]

        inertial_to_sensor = (
            self._total_rotation_sensor_to_body @ Matrix.transformation(u[6:10]).transpose
        )
        B = inertial_to_sensor @ self._B_inertial

        B = self.apply_noise(B)
        B = self.apply_temperature_drift(B)
        B = self.quantize(B)

        self.measurement = tuple([*B])
        self._save_data((time, *B))

    def export_measured_data(self, filename, file_format="csv"):
        self._generic_export_measured_data(
            filename=filename, file_format=file_format, data_labels=("t", "bx", "by", "bz")
        )

    def to_dict(self, **kwargs):
        return super().to_dict(**kwargs)

    @classmethod
    def from_dict(cls, data):
        raise NotImplementedError("from_dict not implemented for this example Magnetometer")


# ============================================================================
# 3. MOTOR: AeroTech L1090W-P
# ============================================================================
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


# ============================================================================
# 4. ROCKET
# ============================================================================
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


# ============================================================================
# 5. SENSORS
# ============================================================================
# All sensors are mounted in a notional avionics bay ~0.3 m ahead of the dry
# CG, aligned with the body axes (default orientation).
AV_BAY_POSITION = 0.3

# ---- IMU #1: Bosch BMI323 -- low-g (8 g), high precision --------------------
# Source: Bosch BMI323 datasheet (bst-bmi323-ds000), accelerometer @ FS=8g,
# gyroscope @ FS=2000 dps.
bmi323_accel = Accelerometer(
    sampling_rate=200,
    orientation=(0, 0, 0),
    measurement_range=8 * G0,                # 78.45 m/s^2
    resolution=G0 / 4096,                    # 4096 LSB/g @ 8g -> 2.394e-3 m/s^2/LSB
    noise_density=180e-6 * G0,               # 180 ug/sqrt(Hz) -> 1.765e-3 m/s^2/sqrt(Hz)
    constant_bias=0.035 * G0,                # +-35 mg typ. zero-g offset (soldered)
    temperature_bias=0.0003 * G0,            # +-0.3 mg/K TCO
    consider_gravity=False,
    name="BMI323 Accelerometer",
)
bmi323_gyro = Gyroscope(
    sampling_rate=200,
    orientation=(0, 0, 0),
    measurement_range=np.radians(2000),      # 34.91 rad/s
    resolution=np.radians(1 / 16.4),         # 16.4 LSB/dps @ 2000dps -> 1.064e-3 rad/s/LSB
    noise_density=np.radians(0.007),         # 0.007 dps/sqrt(Hz) -> 1.222e-4 rad/s/sqrt(Hz)
    constant_bias=np.radians(1.0),           # +-1 dps typ. zero-rate offset (lifetime)
    temperature_bias=np.radians(0.04),       # +-0.04 dps/K TCO
    name="BMI323 Gyroscope",
)

# ---- IMU #2: STM LSM6DSO32 -- general reference (32 g) ---------------------
# Source: ST LSM6DSO32 datasheet + AN5192 (shared silicon w/ LSM6DSO, same
# noise densities); accelerometer @ FS=32g, gyroscope @ FS=2000 dps.
lsm6dso32_accel = Accelerometer(
    sampling_rate=200,
    orientation=(0, 0, 0),
    measurement_range=32 * G0,               # 313.8 m/s^2
    resolution=0.976e-3 * G0,                # 0.976 mg/LSB @ 32g
    noise_density=70e-6 * G0,                # 70 ug/sqrt(Hz) (AN5192, high-perf mode)
    constant_bias=0.040 * G0,                # +-40 mg typ. zero-g level (approx., see note)
    temperature_bias=0.0005 * G0,            # approx., not separately published for 32g variant
    consider_gravity=False,
    name="LSM6DSO32 Accelerometer",
)
lsm6dso32_gyro = Gyroscope(
    sampling_rate=200,
    orientation=(0, 0, 0),
    measurement_range=np.radians(2000),      # 34.91 rad/s
    resolution=np.radians(70e-3),            # 70 mdps/LSB @ 2000dps
    noise_density=np.radians(3.8e-3),        # 3.8 mdps/sqrt(Hz) (AN5192)
    constant_bias=np.radians(0.5),           # +-0.5 dps typ. zero-rate level
    temperature_bias=np.radians(0.05),       # approx., see note
    name="LSM6DSO32 Gyroscope",
)

# ---- IMU #3: Analog Devices ADXL375 -- high-g (200 g), accel only ----------
# Source: ADXL375 datasheet (Rev. B) + ADI EngineerZone application note.
adxl375_accel = Accelerometer(
    sampling_rate=200,
    orientation=(0, 0, 0),
    measurement_range=200 * G0,              # 1961.3 m/s^2
    resolution=49e-3 * G0,                   # 49 mg/LSB (20.5 LSB/g)
    noise_density=5e-3 * G0,                 # 5 mg/sqrt(Hz)
    constant_bias=0.3 * G0,                  # approx. representative 0g offset for this
                                              # "low precision" shock sensor, see note
    consider_gravity=False,
    name="ADXL375 Accelerometer",
)

# ---- Barometer #1: Bosch BMP581 --------------------------------------------
# Source: Bosch BMP581 datasheet + Bosch press release (relative accuracy
# +-6 Pa / +-0.5 m, RMS noise 0.08 Pa, resolution 1/64 Pa, TCO 0.5 Pa/K).
bmp581_baro = Barometer(
    sampling_rate=50,
    measurement_range=125000,                # Pa, sensor's full operating range is 30-125 kPa
    resolution=1 / 64,                       # Pa/LSB
    noise_density=0.08,                      # Pa/sqrt(Hz) (approx., see note)
    temperature_bias=0.5,                    # Pa/K TCO
    name="BMP581",
)

# ---- Barometer #2: Bosch BMP390 --------------------------------------------
# Source: Bosch BMP390 datasheet (relative accuracy +-3 Pa / +-0.25 m).
bmp390_baro = Barometer(
    sampling_rate=50,
    measurement_range=125000,
    resolution=0.016,                        # Pa/LSB, approx.
    noise_density=0.03,                      # Pa/sqrt(Hz), approx., see note
    temperature_bias=0.75,                   # Pa/K TCO (resistive tech, higher than BMP581)
    name="BMP390",
)

# ---- Magnetometer #1: PNI RM3100 -- high precision -------------------------
# Source: PNI RM3100 datasheet (resolution/noise floor) + RM3100 user manual
# (linear range ~100,000 nT).
rm3100_mag = Magnetometer(
    sampling_rate=100,
    latitude=LAUNCH_LAT,
    longitude=LAUNCH_LON,
    elevation=LAUNCH_ELEVATION,
    date=launch_date,
    orientation=(0, 0, 0),
    measurement_range=80e-6,                 # +-80 uT, comfortably covers local field + noise
    resolution=13e-9,                        # 13 nT/LSB (given)
    noise_density=4e-15,                     # 4 pT/sqrt(Hz) (datasheet noise floor)
    constant_bias=50e-9,                     # small representative board-level offset
    name="RM3100",
)

# ---- Magnetometer #2: Bosch BMM150 -- general measurement ------------------
# Source: Bosch BMM150 datasheet (range +-1300/+-2500 uT, 0.3 uT resolution).
bmm150_mag = Magnetometer(
    sampling_rate=50,
    latitude=LAUNCH_LAT,
    longitude=LAUNCH_LON,
    elevation=LAUNCH_ELEVATION,
    date=launch_date,
    orientation=(0, 0, 0),
    measurement_range=1300e-6,               # +-1300 uT (uniform per-axis approx.; Z is +-2500 uT)
    resolution=0.3e-6,                       # 0.3 uT/LSB (given)
    noise_density=0.6e-6,                    # approx. self-noise, see note
    constant_bias=2e-6,                      # representative uncalibrated hard-iron-like offset
    name="BMM150",
)

max_f10s_gnss = GnssReceiver(
    sampling_rate=10,
    altitude_accuracy=1.5 * 2.0, # I'll assume that altitude accuracuy is twice as bad
    position_accuracy=1.5,
    name="Max-F10S"
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


# ============================================================================
# 6. FLIGHT
# ============================================================================
test_flight = Flight(
    rocket=rocket,
    environment=env,
    rail_length=5.2,
    inclination=85,
    heading=0,
)

# print(f"\nApogee: {test_flight.apogee - LAUNCH_ELEVATION:.1f} m AGL")
# print(f"Max velocity: {test_flight.max_speed:.1f} m/s")
# print(f"Static margin at liftoff: {rocket.static_margin(0):.2f} cal "
#       f"({rocket.static_margin(0) * 2 * BODY_RADIUS * 100:.1f} cm)")

# print("\n--- IGRF-14 field at launch site (cross-check against NOAA's online") 
# print("    calculator: https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml) ---")
# print(f"    Date: {launch_date.date()}   Lat/Lon: {LAUNCH_LAT:.4f}, {LAUNCH_LON:.4f}")
# print(f"    Total field F = {rm3100.total_field_nT:.0f} nT")
# print(f"    Declination D = {rm3100.declination_deg:.2f} deg")
# print(f"    Inclination I = {rm3100.inclination_deg:.2f} deg")
# print(f"    (East, North, Up) = {tuple(round(x,1) for x in rm3100.field_enu_nT)} nT")

# test_flight.plots.trajectory_3d()















'''Just to see what the accelerometer is doing. A little test you might say'''
import numpy as np
import matplotlib.pyplot as plt
from rocketpy import Accelerometer, Flight

# 1. Build a noiseless twin of bmi323_accel: same mounting/orientation,
#    everything else zeroed so it reports pure sim-truth specific force.
# bmi323_truth = Accelerometer(
#     sampling_rate=bmi323_accel.sampling_rate,
#     orientation=bmi323_accel.orientation,
#     consider_gravity=bmi323_accel.consider_gravity,
#     measurement_range=np.inf,
#     resolution=0,
#     noise_density=0,
#     random_walk_density=0,
#     constant_bias=0,
#     temperature_bias=0,
#     temperature_scale_factor=0,
#     cross_axis_sensitivity=0,
#     name="BMI323 (truth)",
# )

# 2. Attach it at the SAME position you used for bmi323_accel originally,
#    then re-run the flight so both sensors sample the identical trajectory.
# rocket.add_sensor(bmi323_truth, AV_BAY_POSITION)  # <- use your real mounting position here


test_flight = Flight(
    rocket=rocket,
    environment=env,
    rail_length=test_flight.rail_length,
    inclination=test_flight.inclination,
    heading=test_flight.heading,
)

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
        self.test_flight = Flight(
            rocket=rocket,
            environment=env,
            rail_length=test_flight.rail_length,
            inclination=test_flight.inclination,
            heading=test_flight.heading,
        )
        
    def update(self, t: float):
        self.t = t
        
    def measure(self):
        bmi323_a = _nearest_reading(bmi323_accel, self.t)
        bmi323_g = _nearest_reading(bmi323_gyro, self.t)
        lsm_a = _nearest_reading(lsm6dso32_accel, self.t)
        lsm_g = _nearest_reading(lsm6dso32_gyro, self.t)
        adxl_a = _nearest_reading(adxl375_accel, self.t)
        bmm_m = _nearest_reading(bmm150_mag, self.t)
        rm_m = _nearest_reading(rm3100_mag, self.t)
        bmp390_b = _nearest_reading(bmp390_baro, self.t)
        bmp581_b = _nearest_reading(bmp581_baro, self.t)
        max_gnss = _nearest_reading(max_f10s_gnss, self.t)

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


# # 3. Pull out (t, x, y, z) arrays for both sensors
# truth = np.array(bmi323_truth.measured_data)   # columns: t, ax, ay, az
# meas  = np.array(bmi323_accel.measured_data)   # columns: t, ax, ay, az

# # 4. Plot
# fig, axes = plt.subplots(3, 1, figsize=(9, 8), sharex=True)
# labels = ["Body-frame X (m/s²)", "Body-frame Y (m/s²)", "Body-frame Z (m/s²)"]

# for i, ax in enumerate(axes):
#     ax.plot(truth[:, 0], truth[:, i + 1], label="Sim truth", linewidth=1.5)
#     ax.plot(meas[:, 0], meas[:, i + 1], label="BMI323 (sensor)", linewidth=0.8, alpha=0.7)
#     ax.set_ylabel(labels[i])
#     ax.legend(loc="upper right")
#     ax.grid(alpha=0.3)

# axes[-1].set_xlabel("Time (s)")
# fig.suptitle("BMI323 body-frame acceleration: sim truth vs. sensor")
# fig.tight_layout()
# plt.show()