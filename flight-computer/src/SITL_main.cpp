//////////////////////////////////////////////////////////////////
//
//    SITL_main.cpp -- Core HawkSITL driver. WARNING: Do NOT touch 
//    unless you know what you're doing!!
//
//////////////////////////////////////////////////////////////////

#include <stdio.h>
#include <format>
#include <iostream>
#include <math.h>

#include "framework/core/toml.hpp"
#include "framework/core/IPC_environment.hpp"
#include "framework/core/flight_main.hpp"

int main() {
    /// Determine IPC port from sim-config.toml
    toml::table toml_tbl = toml::parse_file("sim-config.toml");
    int IPC_port = toml_tbl["IPC_port"].value_or(5400);

    /// Initiate computer<-->environment IPC
    IPC_Environment ipc;
    ipc.start(IPC_port);

    /// Run flight setup as soon as sensor data becomes available
    while (true) {
        /// Try to receive environment data (usually sensor data)
        std::optional<json> sensor_data_opt = (ipc).recvJSON();
        if (!sensor_data_opt)
            continue;
        
        /// Execute setup and get a control step back (if provided)
        ControlStep control_step = setup(*sensor_data_opt);    
        
        /// Send the control step back to the environment 
        ipc.sendJSON({
            {"control_msg", control_step.control_msg},
            {"dt", control_step.execution_time}
        });
        // Beak now that setup has succesfully completed
        break;
    }

    /// Execute control loop
    while (true) {
        /// Try to receive sensor data
        std::optional<json> sensor_data_opt = (ipc).recvJSON();
        if (!sensor_data_opt)
            continue;
        
        /// Execute this control step
        ControlStep control_step = loop(*sensor_data_opt);    
        
        /// Send the control step back to the environment 
        ipc.sendJSON({
            {"control_msg", control_step.control_msg},
            {"dt", control_step.execution_time}
        });
    }

    return 0;
}