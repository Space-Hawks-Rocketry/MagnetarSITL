#include "framework/core/flight_main.hpp"

/// Treat these functions like the Arduino setup() and loop() functions. Sensor data
/// is given to you out-of-the-box instead of through your sensor firmware.

const float LOOP_DT = 0.01;

ControlStep setup(json sensor_data) {
    return {.control_msg = {}, .execution_time = 0.01};
}

ControlStep loop(json sensor_data) {
    return {.control_msg = {}, .execution_time = LOOP_DT};
}