from time import sleep
from datetime import datetime
from threading import Thread
from gpiozero import MotionSensor


def main():
    # Configuration:
    time_between_sending_data = 300

    # End config

    motion_sensor_count = -1
    try:
        motion_sensor = MotionSensor(1)  # Sensor plugged into GPIO###
    except MotionSensor.GPIOZeroError:
        log_error("GPIOZero Error on initialising sensor")
        end
    except:
        log_error("Error initialising sensor")

    # Make a new thread to run every Nth minute to off-load the data 
    new_thread = Thread(target=send_data(motion_sensor_count, time_between_sending_data),args={})
    new_thread.start()

    # Main loop.
    while (True):
        motion_sensor_count = start_sensors()
        if motion_sensor_count < 0:  # Sensors are not started.
            sleep(1)
            continue
        motion_sensor.wait_for_motion()
        motion_sensor_count += 1

    


def start_sensors():
    # if no sensors attached, return, or try catch and log error?
    # if sensors already active, return
    # start sensors
    # return
    return 0


def send_data(motion_sensor_count, time_between_sending_data):
    if motion_sensor_count == -1: return
    #do the send thing here
    motion_sensor_count = 0
    sleep(time_between_sending_data)
    return



def log_error(error):
    if error == None: return
    if error == "": return
    now = datetime.now()
    date = now.strftime("d/%m/%Y")
    nowtime = now.strftime("%H:%M:%S")
    with open(date + " sensor error log", 'a') as log:
        log.write(now + " " + error)
    return



if __name__ == '__main__':
    print()
    main()