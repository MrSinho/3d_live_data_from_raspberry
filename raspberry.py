import time
from datetime import datetime
import socket
import Adafruit_ADXL345

accel = Adafruit_ADXL345.ADXL345()

s = socket.socket()
host = "192.168.1." # <-- Edit this
print(host)
port = 8080

print("waiting for incoming connections")
s.bind((host, port))
s.listen(1)
conn, addr = s.accept()
print("connected to " + str(addr))

#Description from Tony Nicola:
# Alternatively you can specify the device address and I2C bus with parameters:
#accel = Adafruit_ADXL345.ADXL345(address=0x54, busnum=2)

# You can optionally change the range to one of:
#  - ADXL345_RANGE_2_G   = +/-2G (default)
#  - ADXL345_RANGE_4_G   = +/-4G
#  - ADXL345_RANGE_8_G   = +/-8G
#  - ADXL345_RANGE_16_G  = +/-16G
# For example to set to +/- 16G:
#accel.set_range(Adafruit_ADXL345.ADXL345_RANGE_16_G)

# Or change the data rate to one of:
#  - ADXL345_DATARATE_0_10_HZ = 0.1 hz
#  - ADXL345_DATARATE_0_20_HZ = 0.2 hz
#  - ADXL345_DATARATE_0_39_HZ = 0.39 hz
#  - ADXL345_DATARATE_0_78_HZ = 0.78 hz
#  - ADXL345_DATARATE_1_56_HZ = 1.56 hz
#  - ADXL345_DATARATE_3_13_HZ = 3.13 hz
#  - ADXL345_DATARATE_6_25HZ  = 6.25 hz
#  - ADXL345_DATARATE_12_5_HZ = 12.5 hz
#  - ADXL345_DATARATE_25_HZ   = 25 hz
#  - ADXL345_DATARATE_50_HZ   = 50 hz
#  - ADXL345_DATARATE_100_HZ  = 100 hz (default)
#  - ADXL345_DATARATE_200_HZ  = 200 hz
#  - ADXL345_DATARATE_400_HZ  = 400 hz
#  - ADXL345_DATARATE_800_HZ  = 800 hz
#  - ADXL345_DATARATE_1600_HZ = 1600 hz
#  - ADXL345_DATARATE_3200_HZ = 3200 hz
# For example to set to 6.25 hz:

#accel.set_data_rate(Adafruit_ADXL345.ADXL345_DATARATE_0_39_HZ)
accel.set_data_rate(Adafruit_ADXL345.ADXL345_DATARATE_6_25HZ)

datetime = str(datetime.now())
filename = open("filename.nmspmm", "w")
filename.write(datetime)
filename.flush()
filename.close()
filename = open("filename.nmspmm", "rb")
filename_data = filename.read(9999999)
conn.send(filename_data)
print("filename has been sent...")

_time = 0.16

unit = 1
def begin():
    input_unit = input(str("Choose the accelleration unit: \n [1]: g(=1/9.8 m/s2) \n [2]: m/s2(=9.8 g)\n"))
    if input_unit == "1": unit = 1
    elif input_unit == "2": unit = 9.8
    else: begin()
begin()

while True:
    # Read the X, Y, Z axis acceleration values and print them.
    x, y, z = accel.read()*unit
    x = 1/2*x*(_time*_time)
    y = 1/2*y*(_time*_time)
    z = 1/2*z*(_time*_time)
    file = open(f"Data/{datetime}data.spmm", "w")
    data = (f"{x} {y} {z} ")
    file.write(data)
    file = open(f"Data/{datetime}data.spmm", "rb")
    filedata = file.read(9999999)
    conn.send(filedata)
    file.flush()
    print(str(data))
    time.sleep(_time)
    file.close()
