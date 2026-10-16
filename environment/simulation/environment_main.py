from framework.core.SITL_handle import SITLHandle
## ------------------------------------------
## Entry point to the user-defined environment simulation.
## ------------------------------------------
from .models.rockets.magnetar import MagnetarRocket

import numpy as np
import matplotlib.pyplot as plt

rocket = MagnetarRocket()
from .models.magnetar.magnetar_model import MagnetarModel
magnetar = MagnetarModel()

reported_t = []
reported_att_x = []
flip_flop = False
  
def SITL_setup(sitl: SITLHandle):
  '''Called before starting simulation. Use this to schedule events.'''
  
  #sitl.scheduleAtTime(5, name_of_function)
  
  
  pass
  print("\nSTATUS: Running SITL simulation...")

def SITL_physicsUpdate(sitl: SITLHandle, t: float, dt: float):
  '''Called at each time step. Use this to integrate models forward in time.'''
  magnetar.update(t)
  
  # write to truth_log
  altitude = magnetar.flight.z(t)
  truth_log.write(f"{t},{altitude}\n")

def SITL_controlUpdate(sitl: SITLHandle, control_msg: dict):
  '''Called when a control message is received from the simulated flight computer. 
    The control_msg contents is defined by flight_main.cpp.'''
    
   
  if "report" in control_msg:
    
    # add report data to numpy array
    
    global flip_flop
    
    reported_t.append(control_msg["t"])
    
    if flip_flop == False:
      reported_att_x.append(control_msg["report"]["att_est"]["x"])
      flip_flop = True
    else:
      reported_att_x.append(np.nan)
      flip_flop = False
    
  if "deploy_parachute" in control_msg:
    if control_msg["deploy_parachute"] == True:
      pass
      # deploy parachute

def SITL_createSensorData(sitl: SITLHandle) -> dict:
  '''Must return sensor data to be parsed by the simulated flight computer.
    Returned dict structure is defined here and utilized by flight_main.cpp.'''
  return magnetar.measure()

def SITL_finish(sitl: SITLHandle):
  '''Called immediately before stopping the simulation.'''
  print("STATUS: Finished SITL simulation.")
  
  plt
  plt.plot(reported_t, reported_att_x, 'r*')
  plt.show()
  
  magnetar.flight.altitude()
  # close truth_log
  truth_log.close()