"""add in description
"""


import string
from time import sleep
from datetime import datetime
from threading import Thread
from gpiozero import MotionSensor


def main() -> None:
    # Configuration:  
    time_between_sending_data = 300

    # End config.  

    motion_sensor_count = -1
    try:
        motion_sensor = MotionSensor(1)  # Sensor plugged into GPIO###  
        motion_sensor_count = 0  # Shows motion sensor is ready.  
    except MotionSensor.GPIOZeroError:
        log_entry("GPIOZero Error on initialising sensor")
        quit
    except:
        log_entry("Error initialising sensor")
        quit

    # Make a new thread to run every Nth minute to off-load the data.  
    new_thread = Thread(target=send_data(motion_sensor_count, time_between_sending_data),args={})
    new_thread.start()

    # Main loop. Count each signal from the motion sensor.  
    while (True):
        if motion_sensor_count == -1:  # Sensors are not started.  
            sleep(1)
            continue
        motion_sensor.wait_for_motion()
        motion_sensor_count += 1


"""Send motion sensor data to XX. No return."""
def send_data(motion_sensor_count: int, time_between_sending_data: int) -> None:
    if motion_sensor_count == -1: return
    try:
        #do the send thing here
        motion_sensor_count = 0
    except:
        log_entry("failed logging count of ", motion_sensor_count)
    sleep(time_between_sending_data)
    return


"""Append a timestamp + message to the dated log file."""
def log_entry(message: string) -> None:
    if message == None: return
    if message == "": return
    now = datetime.now()
    date = now.strftime("d/%m/%Y")
    nowtime = now.strftime("%H:%M:%S")
    with open(date + " sensor log", 'a') as log:
        log.write(now + " " + message)
    return


if __name__ == '__main__':
    main()