import csv
## ------------------------------------------
## Defines empty_packet(); returns an empty dict (a "packet") to hold rows of flight data
## Defines a mapping from column headers into the packet structure
## Defines assign(); populates packet according to instructions from mapping
## Defines stream_csv(); allows for streaming flight log data for arbitrary length logs
## ------------------------------------------

# Going forward, we need to explicitly state the format of the flight logs; amount and order of data, 
## header names, delimiter characters, etc. Then we can adjust this code to match that standard.

# Elapsed Time(ms)	GPS Hour(h)	GPS Minute(min)	GPS Second(s)	GPS Valid(bit)	GPS Fix Type(bit)	GPS Satellites Number	GPS Vertical Height Accuracy (mm)	GPS Height(mm)	GPS Vertical Velocity(mm/s)
# GPS North Velocity(mm/s)	GPS East Velocity(mm/s)	GPS Ground Speed Accuracy(mm/s)	GPS Ground Speed(mm/s)	GPS Longitude(deg*1e-7)	GPS Latitude(deg*1e-7)	
# BMI323 X-Acceleration(m/s)	BMI323 Y-Acceleration(m/s)	BMI323 Z-Acceleration(m/s)	LSM6DSO32 X-Acceleration(m/s)	LSM6DSO32 Y-Acceleration(m/s)	LSM6DSO32 Z-Acceleration(m/s)	
# ADXL375 X-Acceleration(m/s)	ADXL375 Y-Acceleration(m/s)	ADXL375 Z-Acceleration(m/s))	BMI323 X-Angular Rate(deg/s)	BMI323 Y-Angular Rate(deg/s)	BMI323 Z-Angular Rate(deg/s)	
# LSM6DSO32 X-Angular Rate(deg/s)	LSM6DSO32 Y-Angular Rate(deg/s)	LSM6DSO32 Z-Angular Rate(deg/s)	BMM150 X-Field Strength(T*1e-6)	BMM150 Y-Field Strength(T*1e-6)	BMM150 Z-Field Strength(T*1e-6)	
# BMP585 Pressure(Pa)	BMP390 Pressure(Pa)	BMP585 Temperature(deg-C)	BMP585 Temp(deg-C)	Main Battery Voltage(V)	Pyro Battery Voltage(V)	
# Pyro 0 Continuity(V)	Pyro 0 Status	Pyro 1 Continuity(V)	Pyro 1 Status(bit)


def empty_packet():     # I have grouped this data as best as I could to make it easy to parse
    return {
            "timestamp": None,
            "gps": {
                "hour": None,
                "min": None,
                "sec": None,
                "valid": None,
                "fix_type": None,
                "satellite_number": None,
                "vert_height_accuracy": None,
                "height": None,
                "vert_vel": None,
                "north_vel": None,
                "east_vel": None,
                "ground_speed_accuracy": None,
                "ground_speed": None,
                "longitude": None,
                "latitude": None         
            },
            
            "bmi323": {
                "accel": {"x" : None, "y" : None, "z": None},
                "gyro": {"x" : None, "y" : None, "z": None}
            },
            
            "lsm6dso32": {
                "accel": {"x" : None, "y" : None, "z": None},
                "gyro": {"x" : None, "y" : None, "z": None}
            },
            
            "adxl375": {
                "accel": {"x" : None, "y" : None, "z": None},
            },
            
            "bmm150": {
                "mag": {"x" : None, "y" : None, "z": None},
            },
            
            "bmp390": {
                "baro": None,
                "temp": None
            },
            
            "bmp585": {
                "baro": None,
                "temp": None
            },
            
            "main_battery": None,
            "pyro": {
                "battery": None,
                "pyro_0_continuity": None,
                "pyro_0_status": None,
                "pyro_1_continuity": None,
                "pyro_1_status": None
            }
    }

## maps from headers of flight log into the packet structure above
## if headers of flight log change, mapping must change also

mapping = {     
"Elapsed Time(ms)" : ("timestamp", int),

"GPS Hour(h)" : ("gps.hour", int),
"GPS Minute(min)" : ("gps.min", int),
"GPS Second(s)" : ("gps.sec", int),
"GPS Valid(bit)" : ("gps.valid", lambda v : int(v, 16)), # gps valid is a bit mask given in hex
"GPS Fix Type(bit)" : ("gps.fix_type", int), # we need to ask if this field is also hex
"GPS Satellites Number" : ("gps.satellite_number", int),
"GPS Vertical Height Accuracy (mm)" : ("gps.vert_height_accuracy", float),
"GPS Height(mm)" : ("gps.height", float),
"GPS Vertical Velocity(mm/s)" : ("gps.vert_vel", float),
"GPS North Velocity(mm/s)" : ("gps.north_vel", float),
"GPS East Velocity(mm/s)" : ("gps.east_vel", float),
"GPS Ground Speed Accuracy(mm/s)" : ("gps.ground_speed_accuracy", float),
"GPS Ground Speed(mm/s)" : ("gps.ground_speed", float),
"GPS Longitude(deg*1e-7)" : ("gps.longitude", lambda v: float(v) * 1e-7), # convert latitude and longitude to decimal degrees
"GPS Latitude(deg*1e-7)" : ("gps.latitude", lambda v: float(v) * 1e-7),

"BMI323 X-Acceleration(m/s)" : ("bmi323.accel.x", float),
"BMI323 Y-Acceleration(m/s)" : ("bmi323.accel.y", float),
"BMI323 Z-Acceleration(m/s)" : ("bmi323.accel.z", float),

"LSM6DSO32 X-Acceleration(m/s)" : ("lsm6dso32.accel.x", float),
"LSM6DSO32 Y-Acceleration(m/s)" : ("lsm6dso32.accel.y", float),
"LSM6DSO32 Z-Acceleration(m/s)" : ("lsm6dso32.accel.z", float),

"ADXL375 X-Acceleration(m/s)" :  ("adxl375.accel.x", float),
"ADXL375 Y-Acceleration(m/s)" :  ("adxl375.accel.y", float),
"ADXL375 Z-Acceleration(m/s)" :  ("adxl375.accel.z", float),

"BMI323 X-Angular Rate(deg/s)" : ("bmi323.gyro.x", float),
"BMI323 Y-Angular Rate(deg/s)" : ("bmi323.gyro.y", float),
"BMI323 Z-Angular Rate(deg/s)" : ("bmi323.gyro.z", float),

"LSM6DSO32 X-Angular Rate(deg/s)" : ("lsm6dso32.gyro.x", float),
"LSM6DSO32 Y-Angular Rate(deg/s)" : ("lsm6dso32.gyro.y", float),
"LSM6DSO32 Z-Angular Rate(deg/s)" : ("lsm6dso32.gyro.z", float),

"BMM150 X-Field Strength(T*1e-6)" : ("bmm150.mag.x", float),
"BMM150 Y-Field Strength(T*1e-6)" : ("bmm150.mag.y", float),
"BMM150 Z-Field Strength(T*1e-6)" : ("bmm150.mag.z", float),

"BMP585 Pressure(Pa)" : ("bmp585.baro", float),
"BMP390 Pressure(Pa)" : ("bmp390.baro", float),                 

"BMP585 Temp(deg-C)" : ("bmp585.temp", float),
"BMP390 Temp(deg-C)" : ("bmp390.temp", float),                  

"Main Battery Voltage(V)" : ("main_battery", float),

"Pyro Battery Voltage(V)" : ("pyro.battery", float),
"Pyro 0 Continuity(V)" : ("pyro.pyro_0_continuity", float),
"Pyro 0 Status" : ("pyro.pyro_0_status", int), # single bit; 0 or 1
"Pyro 1 Continuity(V)" : ("pyro.pyro_1_continuity", float),
"Pyro 1 Status(bit)" : ("pyro.pyro_1_status", int) # single bit

}
   
def assign(packet, path, value):

    # this function parses the dot path to navigate packet structure; Example:
    # "BMI323 X-Acceleration(m/s)" : ("accel.BMI323.x", float),
    # value in column "BMI323 X-Acceleration(m/s)" is stored at packet["accel"]["BMI323"]["x"]

    keys = path.split(".")
    d = packet
    for k in keys[:-1]:
        d = d[k]
    d[keys[-1]] = value

def stream_csv(path):

    # Test.dat has about 15 seconds of flight data and is 512MB; we have to stream data line-by-line;
    # this is accomplished using yield.

    with open(path, "r") as f:
        reader = csv.DictReader(f, delimiter="\t") # for .csv data, set delimiter=","

        for row in reader:
            packet = empty_packet()

            for csv_col, (path, transform) in mapping.items():
                raw_value = row[csv_col]
                value = transform(raw_value)
                assign(packet, path, value)

            yield packet

###############
# for row in reader:
#   

