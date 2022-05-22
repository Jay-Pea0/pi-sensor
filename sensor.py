"""add in description
"""

import sys                              # Used for command line arguments.
import getopt                           # Used to parse command line arguments.
import requests                         # Used for HTML POST requests.
from os         import path             # Used for file logging.
from datetime   import datetime         # Used for log files.
from time       import sleep            # Used for timing sending data.
from threading  import Thread           # Used for multi-threading (for timing).
from gpiozero   import MotionSensor     # Used for motion sensor.
import RPi.GPIO as GPIO                 # Used for IR distance sensor.


def main(argv: list) -> None:
    # Defaults 
    interval = 300  # 5 mins default.
    pin = 1
    data = {
        "WEB_URL":"http://pastebin.com/api/api_post.php",
        "KEY":"XXXXXXXXXXXXXXXXX",
        "count":-1
    }
    # End config.  

    help_statement = str(argv[0]) + " -s <motion|ir> -p <pin #> -i <interval/s>"
    try:
       opts, args = getopt.getopt(argv[1:],"hs:p:i:",["sensor=","pin=","interval="])
    except getopt.GetoptError:
       print(help_statement)
       sys.exit(2)

    if len(argv) <= 1:
        print("Not enough arguments. Exiting...")
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            print(help_statement)
            sys.exit()
        elif opt in ("-s", "--sensor"):
            sensor_type = arg
            if sensor_type == "motion": continue
            elif sensor_type == "ir": continue
            else:
                print("Invalid sensor. " + help_statement)
                sys.exit()
        elif opt in ("-p", "--pin"):
            pin = arg
            try:
                pin = int(pin)
            except:
                print("Pin must be a whole number.")
                sys.exit()
            if pin < 0:
                print("Pin must be a positive number.")
                sys.exit()
        elif opt in ("-i", "--interval"):
            interval = arg
            try:
                interval = int(interval)
            except:
                print("Interval must be a whole number.")
                sys.exit()
            if interval < 1:
                print("Interval of " + str(interval) + "is too short.")
                sys.exit()
            if interval > 600:
                if input("Confirm interval of " + str(interval) + " (y): ") != 'y':
                    sys.exit() 

    # Make a new thread to run every Nth second to off-load the data.  
    new_thread = Thread(target=send_data(data, interval),args={})
    new_thread.start()

    # Main loop. Count each signal from the motion sensor.  
    while (True):
        # Check sensors are started, extra guarding.
        if data["count"] == -1:
            if sensor_type == "motion":
                sensor, data = start_motion_sensor(pin, data)
            elif sensor_type == "ir":
                sensor, data = start_ir_sensor(pin, data)  
            sleep(1)
            continue
        if sensor_type == "motion":
            sensor.wait_for_motion()
            data["count"] += 1
            print("count=" + str(data['count']))
        elif sensor_type == "ir":
            if GPIO.input(pin):
                data["count"] += 1
                print("count=" + str(data['count']))
            else:
                sleep(0.5)
            
        


def start_motion_sensor(pin: int, data: dict) -> tuple:
    """Attempts to start the motion sensor.
    Initialises count to 0.
    Returns sensor and data dictionary.
    """
    try:
        sensor = MotionSensor(pin)  
        data["count"] = 0  # Shows motion sensor is ready.  
        log_entry("Initialising motion sensor on pin " + str(pin) + ".")
        sleep(60)  # Give sensor time to start.
        log_entry("Initialised motion sensor on pin " + str(pin) + ".")
    except:
        error_msg = "Error initialising motion sensor on pin " + str(pin) + "."
        print(error_msg)
        log_entry(error_msg)
        sys.exit(2)
    return sensor, data



def start_ir_sensor(pin: int, data: dict) -> tuple:
    # Not implemented yet.
    """Attempts to start the IR sensor.
    Initialises count to 0.
    Returns sensor and data dictionary.
    """
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        sensor = GPIO.setup(pin, GPIO.IN)  
        data["count"] = 0  # Shows IR sensor is ready. 
        log_entry("Initialising IR sensor on pin " + str(pin)) 
        sleep(60)
        log_entry("Initialised IR sensor on pin " + str(pin))
    except:
        error_msg = "Error initialising IR sensor on pin " + str(pin) + "."
        print(error_msg)
        log_entry(error_msg)
        sys.exit(2)
    return sensor, data


def send_data(data: dict, interval: int) -> None:
    """Send sensor data to backend. No return."""
    if data["count"] == -1: return  # Sensor not active.
    try:
        r = requests.post(url = data["WEB_URL"], data = data)
        log_entry(r)  # Response from the backend.
        data["count"] = 0
    except:
        log_entry("Failed logging count of " + str(data["count"]) + "Will try again in " + str(interval) + " seconds.")
    sleep(interval)
    return


def log_entry(message: str) -> None:
    """Append a timestamp + message to the dated log file. No return"""
    if message == None: return
    if message == "": return
    now = datetime.now()
    now_date = now.strftime("%d_%m_%Y")
    now_time = now.strftime("%H:%M:%S")
    filename = now_date + " Sensor Log"
    directory = path.dirname(path.realpath(__file__))
    with open(directory + '/' +filename, 'a') as log:
        log.write(now_time + " " + message + "\n")
    return


if __name__ == '__main__':
    argv = ['sensor.py', '-s', 'motion', '-p', '17', '-i', '300']
    main(sys.argv)
