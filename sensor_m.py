"""add in description
"""

from sys import sys                 # Used for command line arguments.
from getopt import getopt           # Used for parse command line arguments.
from time import sleep              # Used for timing sending data.
from datetime import datetime       # Used for log files.
from threading import Thread        # Used for multi-threading (for timing).
from requests import requests       # Used for HTML POST requests.
from gpiozero import MotionSensor   # Used for motion sensor.


def main(argv) -> None:
    # Defaults 
    time_between_sending_data = 300  # 5 mins default.
    pin = 1
    data = {
        "WEB_URL":"http://pastebin.com/api/api_post.php",
        "KEY":"XXXXXXXXXXXXXXXXX",
        "count":-1
    }
    # End config.  

    help_statement = "sensor.py -s <motion|ir> -i <interval/ms>"
    try:
       opts, args = getopt.getopt(argv,"hs:p:i:",["sensor=","pin=","interval="])
    except getopt.GetoptError:
       print(help_statement)
       sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help_statement)
            sys.exit()
        elif opt in ("-s", "--sensor"):
            sensor = arg
            if sensor == "motion": continue
            elif sensor == "ir": continue
            else:
                print("Invalid sensor. ", help_statement)
                sys.exit()
        elif opt in ("-p", "--pin"):
            pin = arg
            if (pin < 1):
                print("Pin set at command line too low: ", pin)
        elif opt in ("-i", "--interval"):
            interval = arg
            if interval < 1:
                print("Interval of ", interval, "is too short.")
                sys.exit()
            if interval > 600:
                if input("Confirm interval of ", interval, "(y): ") != 'y':
                    sys.exit() 

    # Make a new thread to run every Nth second to off-load the data.  
    new_thread = Thread(target=send_data(data, interval),args={})
    new_thread.start()

    # Main loop. Count each signal from the motion sensor.  
    while (True):
        # Check sensors are started, extra guarding.
        if data["count"] == -1:
            if sensor == "motion":
                sensor, data = start_motion_sensor(data)
            elif sensor == "ir":
                sensor, data = start_ir_sensor(data)  
            sleep(1)
            continue
        if sensor == "motion":
            sensor.wait_for_motion()
        elif sensor == "ir":
            pass
        data["count"] += 1


"""Attempts to start the motion sensor.
Initialises count to 0.
Returns sensor and data dictionary.
"""
def start_motion_sensor(pin: int, data: dict) -> tuple(MotionSensor, dict):
    try:
        sensor = MotionSensor(pin)  
        data["count"] = 0  # Shows motion sensor is ready.  
        log_entry("Initialised motion sensor on pin ", pin)
    except MotionSensor.GPIOZeroError:
        log_entry("GPIOZero Error on initialising sensor. Pin: ", pin)
        sys.exit(2)
    except:
        log_entry("Error initialising sensor. Pin: ", pin)
        sys.exit(2)
    return sensor, data


# Not implemented yet.
"""Attempts to start the IR sensor.
Initialises count to 0.
Returns sensor and data dictionary.
"""
def start_ir_sensor(pin: int, data: dict) -> tuple(MotionSensor, dict):
    try:
        sensor = pin  # Sensor plugged into GPIO###  
        data["count"] = 0  # Shows IR sensor is ready.  
        log_entry("Initialised IR sensor on pin ", pin)
    except:
        log_entry("Error initialising sensor")
        sys.exit(2)
    return sensor, data


"""Send sensor data to backend. No return."""
def send_data(WEB_URL: str, data: dict, interval: int) -> None:
    if data["count"] == -1: return  # Sensor not active.
    try:
        r = requests.post(url = WEB_URL, data = data)
        log_entry(r)  # Response from the backend.
        data["count"] = 0
    except:
        log_entry("Failed logging count of ", data["count"], "Will try again in ", interval, " seconds.")
    sleep(interval)
    return


"""Append a timestamp + message to the dated log file. No return"""
def log_entry(message: str) -> None:
    if message == None: return
    if message == "": return
    now = datetime.now()
    now_date = now.strftime("d/%m/%Y")
    now_time = now.strftime("%H:%M:%S")
    with open(now_date + " sensor log", 'a') as log:
        log.write(now_time + " " + message)
    return


if __name__ == '__main__':
    main(sys.argv[1:])