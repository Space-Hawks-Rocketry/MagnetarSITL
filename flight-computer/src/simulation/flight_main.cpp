#include "framework/core/flight_main.hpp"
#include "iostream"
#include "math.h"

/// Treat these functions like the Arduino setup() and loop() functions. Sensor data
/// is given to you out-of-the-box instead of through your sensor firmware.

const float LOOP_DT = 0.01;


// Keaton 10/08/26
#include <fstream>
static std::ofstream log_file("altitude_log.csv");
static float t = 0.0f;



ControlStep setup(json sensor_data) {
    return {.control_msg = {}, .execution_time = 0.01};
}

ControlStep loop(json sensor_data) {
    json control_msg = {};

    // read sensors

    // ex. float P = sensor_data["bmp390"]["baro"];
    float P = sensor_data["bmp390"]["baro"];
    static bool initialized = false;
    static float P0;

    if (!initialized)
    {
        P0 = P;
        initialized = true;
    }

    float h = 44330.0f *
            (1.0f - pow(P / P0, 0.1903f));


    log_file << t
         << ","
         << P
         << ","
         << h
         << "\n";

    t += LOOP_DT;
    
    // estimate state

    // make decisions
    // control_msg["deploy_parachute"] = true;


    // output commands
    return {.control_msg = control_msg, .execution_time = LOOP_DT};
}