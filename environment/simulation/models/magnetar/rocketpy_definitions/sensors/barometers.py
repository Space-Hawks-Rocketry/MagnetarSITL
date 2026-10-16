from rocketpy import Barometer

bmp390_baro = Barometer(
    sampling_rate=50,
    measurement_range=125000,
    resolution=0.016,                        # Pa/LSB, approx.
    noise_density=0.03,                      # Pa/sqrt(Hz), approx., see note
    temperature_bias=0.75,                   # Pa/K TCO (resistive tech, higher than BMP581)
    name="BMP390",
)

bmp581_baro = Barometer(
    sampling_rate=50,
    measurement_range=125000,                # Pa, sensor's full operating range is 30-125 kPa
    resolution=1 / 64,                       # Pa/LSB
    noise_density=0.08,                      # Pa/sqrt(Hz) (approx., see note)
    temperature_bias=0.5,                    # Pa/K TCO
    name="BMP581",
)

truth_baro = Barometer(
    sampling_rate=50,
    name="BMP581",
)