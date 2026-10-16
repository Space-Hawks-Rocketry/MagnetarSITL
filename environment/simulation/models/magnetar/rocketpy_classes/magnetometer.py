
import numpy as np
import ppigrf

from rocketpy.sensors.sensor import InertialSensor
from rocketpy.prints.sensors_prints import _InertialSensorPrints
from rocketpy.mathutils.vector_matrix import Matrix, Vector

class GeomagneticData:
    
    def __init__(self,
                 field_enu_nT,
                 B_inertial,
                 total_field_nT,
                 declination_deg,
                 inclination_deg):
        self.field_enu_nT = field_enu_nT
        self.B_inertial = B_inertial
        self.total_field_nT = total_field_nT
        self.declination_deg = declination_deg
        self.inclination_deg = inclination_deg

# ============================================================================
# CUSTOM MAGNETOMETER SENSOR (IGRF-14 via ppigrf)
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
        geomagnetic_data: GeomagneticData,
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
        soft_iron_matrix=np.identity(3),
        hard_iron_bias=np.zeros((3,1)),
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
        
        self.soft_iron_matrix = soft_iron_matrix
        self.hard_iron_bias = hard_iron_bias
        
        self.field_enu_nT = geomagnetic_data.field_enu_nT
        self._B_inertial = geomagnetic_data.B_inertial
        self.total_field_nT = geomagnetic_data.total_field_nT
        self.declination_deg = geomagnetic_data.declination_deg
        self.inclination_deg = geomagnetic_data.inclination_deg
        
    @staticmethod
    def computeGeomagneticData(elevation,
                               longitude,
                               latitude,
                               date) -> GeomagneticData:
        # --- Evaluate IGRF-14 once at the launch site and cache it (ENU, Tesla) ---
        h_km = elevation / 1000.0
        Be, Bn, Bu = ppigrf.igrf(longitude, latitude, h_km, date)
        Be, Bn, Bu = float(np.asarray(Be).squeeze()), float(np.asarray(Bn).squeeze()), float(np.asarray(Bu).squeeze())
        field_enu_nT = (Be, Bn, Bu)  # stashed for printing/verification
        B_inertial = Vector([Be, Bn, Bu]) * 1e-9  # nT -> T

        # Handy derived quantities for a sanity-check printout against NOAA's
        # online calculator (https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml)
        F = np.sqrt(Be**2 + Bn**2 + Bu**2)
        H = np.sqrt(Be**2 + Bn**2)
        total_field_nT = F
        declination_deg = np.degrees(np.arctan2(Be, Bn))
        inclination_deg = np.degrees(np.arctan2(Bu, H))
        
        return GeomagneticData(field_enu_nT,
                               B_inertial,
                               total_field_nT,
                               declination_deg,
                               inclination_deg)

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
        raise NotImplementedError("from_dict not implemented for this Magnetometer implementation.")