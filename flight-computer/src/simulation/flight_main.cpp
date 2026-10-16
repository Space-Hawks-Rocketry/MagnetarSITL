#include "framework/core/flight_main.hpp"
#include "iostream"
#include "math.h"

/// Treat these functions like the Arduino setup() and loop() functions. Sensor data
/// is given to you out-of-the-box instead of through your sensor firmware.

const float LOOP_DT = 0.01;
static float t = 0.0f;

ControlStep setup(json sensor_data) {
    return {.control_msg = {}, .execution_time = 0.01};
}

ControlStep loop(json sensor_data) {
    json control_msg = {};

    // read sensors
    
    // estimate state

    // make decisions
    // control_msg["deploy_parachute"] = true;

    control_msg["t"] = t;

    json report;

    report["alt_est"]    = 0;    
    report["vert_v_est"] = 0;
    report["vert_a_est"] = 0;

    json att_est;

    att_est["x"] = 0;
    att_est["y"] = 0;
    att_est["z"] = 0;

    report["att_est"] = att_est;


    

    control_msg["report"] = report;

    // output commands
    
    t += LOOP_DT; // step forward
    return {.control_msg = control_msg, .execution_time = LOOP_DT};
}