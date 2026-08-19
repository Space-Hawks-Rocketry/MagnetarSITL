from framework.core.SITL_handle import SITLHandle
from simulation.stream_csv import stream_csv
## ------------------------------------------
## Entry point to the user-defined environment simulation.
## ------------------------------------------

GPS_FREQ_HZ       = 40 #hz
BMI323_FREQ_HZ    = 40 
LSM6DSO32_FREQ_HZ = 40 
ADXL375_FREQ_HZ   = 1 
BMM150_FREQ_HZ    = 40 
BMP390_FREQ_HZ    = 40 
BMP585_FREQ_HZ    = 40 

GPS_SAMPLE_PERIOD_MS       = 1000 / GPS_FREQ_HZ      
BMI323_SAMPLE_PERIOD_MS    = 1000 / BMI323_FREQ_HZ   
LSM6DSO32_SAMPLE_PERIOD_MS = 1000 / LSM6DSO32_FREQ_HZ
ADXL375_SAMPLE_PERIOD_MS   = 1000 / ADXL375_FREQ_HZ  
BMM150_SAMPLE_PERIOD_MS    = 1000 / BMM150_FREQ_HZ   
BMP390_SAMPLE_PERIOD_MS    = 1000 / BMP390_FREQ_HZ   
BMP585_SAMPLE_PERIOD_MS    = 1000 / BMP585_FREQ_HZ   

def SITL_setup(sitl: SITLHandle):
  '''Called before starting simulation. Use this to schedule events.'''

  # for playback of flight logs; specify file to be used
  sitl.packet_stream = stream_csv("environment/flight_logs/Test.dat")
  sitl.log_t0 = None
  sitl.log_t_prev = None
  
  sitl.t_to_next_gps       = GPS_SAMPLE_PERIOD_MS      
  sitl.t_to_next_bmi323    = BMI323_SAMPLE_PERIOD_MS   
  sitl.t_to_next_lsm6dso32 = LSM6DSO32_SAMPLE_PERIOD_MS
  sitl.t_to_next_adxl375   = ADXL375_SAMPLE_PERIOD_MS  
  sitl.t_to_next_bmm150    = BMM150_SAMPLE_PERIOD_MS   
  sitl.t_to_next_bmp390    = BMP390_SAMPLE_PERIOD_MS   
  sitl.t_to_next_bmp585    = BMP585_SAMPLE_PERIOD_MS  

  pass

def SITL_physicsUpdate(sitl: SITLHandle, t: float, dt: float):
  '''Called at each time step. Use this to integrate models forward in time.'''
  pass

def SITL_controlUpdate(sitl: SITLHandle, control_msg: dict):
  '''Called when a control message is received from the simulated flight computer. 
    The control_msg contents is defined by flight_main.cpp.'''
  pass

def SITL_createSensorData(sitl: SITLHandle) -> dict:
  '''Must return sensor data to be parsed by the simulated flight computer.
    Returned dict structure is defined here and utilized by flight_main.cpp.'''

  # playback of flight logs 
  try:
    packet = next(sitl.packet_stream) # get next line from flight log
  except StopIteration: # if no next line
    sitl.stop() # stop
    return {} 
  
  data = {}
  
  t_curr = int(packet["timestamp"])
  
  if sitl.log_t0 == None:
    sitl.log_t0 = t_curr
    sitl.log_t_prev = t_curr  
    
  log_dt = t_curr - sitl.log_t_prev
  sitl.log_t_prev = t_curr
  
  sitl.t_to_next_gps       -= log_dt
  sitl.t_to_next_bmi323    -= log_dt
  sitl.t_to_next_lsm6dso32 -= log_dt
  sitl.t_to_next_adxl375   -= log_dt
  sitl.t_to_next_bmm150    -= log_dt
  sitl.t_to_next_bmp390    -= log_dt
  sitl.t_to_next_bmp585    -= log_dt
  
  if sitl.t_to_next_gps       <= 0:
    data["gps"] = packet["gps"]
    sitl.t_to_next_gps += GPS_SAMPLE_PERIOD_MS

  if sitl.t_to_next_bmi323    <= 0:
    data["bmi323"] = packet["bmi323"]
    sitl.t_to_next_bmi323 += BMI323_SAMPLE_PERIOD_MS

  if sitl.t_to_next_lsm6dso32 <= 0:
    data["lsm6dso32"] = packet["lsm6dso32"]
    sitl.t_to_next_lsm6dso32 += LSM6DSO32_SAMPLE_PERIOD_MS

  if sitl.t_to_next_adxl375   <= 0:
    data["adxl375"] = packet["adxl375"]
    sitl.t_to_next_adxl375 += ADXL375_SAMPLE_PERIOD_MS

  if sitl.t_to_next_bmm150    <= 0:
    data["bmm150"] = packet["bmm150"]
    sitl.t_to_next_bmm150 += BMM150_SAMPLE_PERIOD_MS

  if sitl.t_to_next_bmp390    <= 0:
    data["bmp390"] = packet["bmp390"]
    sitl.t_to_next_bmp390 += BMP390_SAMPLE_PERIOD_MS

  if sitl.t_to_next_bmp585    <= 0:
    data["bmp585"] = packet["bmp585"]
    sitl.t_to_next_bmp585 += BMP585_SAMPLE_PERIOD_MS
  
  return data

  
def SITL_finish(sitl: SITLHandle):
  '''Called immediately before stopping the simulation.'''
  pass




class SupernovaModel:

  def __init__(self):
    '''Read all needed data from csv and find initial time'''
    self.t = 0 # change this to initial time on first row of csv
    self.current_readings = {} # same format as packet

  def update(dt):
    '''Progress supernova model forward in time by dt'''
    self.t += dt
    # get last row data and next row data (as packets), then interpolate between them at this current time
    self.current_raw_sensor_data = 0 # bla bla
    # for each sensor, determine if it is time to read. If time to read, update their respective value in self.current_readings 

  def getSensorReadings():
    # return self.current_readings
    # only return new sensor readings
    pass


def SITL_setup(sitl: SITLHandle):
  '''Called before starting simulation. Use this to schedule events.'''
  pass

def SITL_physicsUpdate(sitl: SITLHandle, t: float, dt: float):
  '''Called at each time step. Use this to integrate models forward in time.'''
  pass

def SITL_controlUpdate(sitl: SITLHandle, control_msg: dict):
  '''Called when a control message is received from the simulated flight computer. 
    The control_msg contents is defined by flight_main.cpp.'''
  pass

def SITL_createSensorData(sitl: SITLHandle) -> dict:
  '''Must return sensor data to be parsed by the simulated flight computer.
    Returned dict structure is defined here and utilized by flight_main.cpp.'''
  return {}
  
def SITL_finish(sitl: SITLHandle):
  '''Called immediately before stopping the simulation.'''
  pass