from framework.core.SITL_handle import SITLHandle
## ------------------------------------------
## Entry point to the user-defined environment simulation.
## ------------------------------------------
from .models.rockets.magnetar import MagnetarRocket

rocket = MagnetarRocket()

# log sim truth
truth_log = open("truth_log.csv", "w")
truth_log.write("time,altitude\n")

def SITL_setup(sitl: SITLHandle):
  '''Called before starting simulation. Use this to schedule events.'''
  pass

def SITL_physicsUpdate(sitl: SITLHandle, t: float, dt: float):
  '''Called at each time step. Use this to integrate models forward in time.'''
  rocket.update(t)
  
  # write to truth_log
  altitude = rocket.test_flight.z(t)
  truth_log.write(f"{t},{altitude}\n")

def SITL_controlUpdate(sitl: SITLHandle, control_msg: dict):
  '''Called when a control message is received from the simulated flight computer. 
    The control_msg contents is defined by flight_main.cpp.'''
  if "deploy_parachute" in control_msg:
    if control_msg["deploy_parachute"] == True:
      pass
      # deploy parachute

def SITL_createSensorData(sitl: SITLHandle) -> dict:
  '''Must return sensor data to be parsed by the simulated flight computer.
    Returned dict structure is defined here and utilized by flight_main.cpp.'''
  return rocket.measure()

def SITL_finish(sitl: SITLHandle):
  '''Called immediately before stopping the simulation.'''
  
  # close truth_log
  truth_log.close() 
  pass