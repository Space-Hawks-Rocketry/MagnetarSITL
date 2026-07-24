##################################################################
##
##    SITL_main.py -- Core HawkSITL driver. WARNING: Do NOT touch 
##    unless you know what you're doing!!
##
##################################################################

from simulation.environment_main import SITL_controlUpdate, SITL_physicsUpdate, SITL_createSensorData, SITL_finish, SITL_setup
from framework.core.IPC_computer import IPC_Computer
from framework.core.SITL_handle import SITLHandle

import tomllib

# Load configuration from sim-config.toml
with open("sim-config.toml", "rb") as f:
    sim_config = tomllib.load(f)

# Start environment<-->computer IPC communication
ipc = IPC_Computer()
ipc.start(sim_config.get("IPC_port", 5400))

# Define simulation parameters
sim_stop_time = sim_config.get("sim_stop_time", 60)
target_dt = sim_config.get("target_dt", 0.01)  # If a computer control step is quicker than this, dt will be smaller
running = True
t = 0

# Create a handle for SITL state to be contorlled by user-defined functions
sitl_handle = SITLHandle(
  stop_delegate=lambda: globals().update(running=False)
)


SITL_setup(sitl_handle) # User-defined setup

# Begin main simulation loop
while running:

  sensor_data = SITL_createSensorData(sitl_handle) # User-defined sensor data
  ipc.sendJSON(sensor_data)
  computer_response = ipc.recvJSON() # User-defined computer control response

  control_msg = computer_response["control_msg"] or {}
  computer_dt = computer_response["dt"]

  SITL_controlUpdate(sitl_handle, control_msg) # User-defined control update handler

  remaining_dt = computer_dt
  while remaining_dt > target_dt:
    actual_t = t + computer_dt - remaining_dt
    
    SITL_physicsUpdate(sitl_handle, actual_t, target_dt) # User-defined physics update
    sitl_handle._update(actual_t, target_dt) # Update handle
    remaining_dt -= target_dt
  actual_t = t + computer_dt - remaining_dt
  SITL_physicsUpdate(sitl_handle, actual_t, remaining_dt) # User-defined physics update
  sitl_handle._update(actual_t, remaining_dt) # Update handle

  t += computer_dt

  if (t >= sim_stop_time) and (sim_stop_time > 0):
    break

SITL_finish(sitl_handle) # User-defined finish handler