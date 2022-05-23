"""Sensor script for Raspberry Pi. Sends to Mongo DB. 
CMP2804M Team Software Engineering - Assignment 3.
"""

import sys                              # Used for command line arguments.
import getopt                           # Used to parse command line arguments.
import pymongo                          # Used for HTML POST request to backend.
from os         import path             # Used for file logging.
from datetime   import datetime         # Used for log files.
from time       import sleep            # Used for timing sending data.
from threading  import Thread           # Used for multi-threading (for timing).
import RPi.GPIO as GPIO                 # Used for sensors.


def main(argv: list) -> None:
    # Defaults - can set at command line.
    interval = 600          # 10 mins.
    pin = 17                
    sensor_type = "motion"  

    # Mongo setup.
    client = pymongo.MongoClient("mongodb+srv://Pi:6ciXdbklDynHHH5i@vanilla.mfxfp.mongodb.net/?retryWrites=true&w=majority")
    db = client.LoneWorking
    col = db["SensorData"]

    # Other.
    data = {
        "timeSent" : "",
        "timeRecieved" : {}
    }
    count = -1

    sensor_type, pin, interval = parse_command_line(argv, sensor_type, pin, interval)


    # Main loop. Count each signal from the motion sensor.  
    while (True):
        # Check sensors are started, extra guarding.
        if count == -1:
            if sensor_type == "motion":
                data, count = start_motion_sensor(data, pin, count)
            elif sensor_type == "ir":
                data, count = start_ir_sensor(data, pin, count)  
            sleep(1)
            continue

        # Save data every minute.
        now_seconds = datetime.now().strftime("%S")
        if now_seconds == "00":
            data, count = save_data(data, count)

        # Send data every ten minutes.
        now_minute = datetime.now().strftime("%M")
        if now_minute[-1] == "0":
            data, count = send_data(data, count)

        if sensor_type == "motion":
            if GPIO.input(pin): 
                count += 1
                print("count=" + str(count))
            sleep(1)

        elif sensor_type == "ir":
            if GPIO.input(pin):
                count += 1
                print("count=" + str(count))
            sleep(1)

def parse_command_line(argv: list, sensor_type: str, pin: int, interval: int) -> tuple:
    """Get the command line arguments, if any.
    Returns tuple of sensor_type, pin, count.
    """
    if len(argv) == 1: return

    # Command line arguments and parsing.
    help_statement = str(argv[0]) + " -s <motion|ir> -p <pin #> -i <interval/s>"

    try:
       opts, args = getopt.getopt(argv[1:],"hs:p:i:",["sensor=","pin=","interval="])

    except getopt.GetoptError:
       print(help_statement)
       sys.exit(2)

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
            
        
def start_motion_sensor(data: dict, pin: int, count: int) -> tuple:
    """Attempts to start the motion sensor.
    Initialises count to 0.
    Returns sensor and data dictionary.
    """
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN)
        count = 0  # Shows motion sensor is ready.

        msg =  "Initialising motion sensor on pin " + str(pin) + "."
        log_entry(msg)
        print(msg)

        sleep(10)  # Give sensor time to start.

        msg = "Initialised motion sensor on pin " + str(pin) + "."
        log_entry(msg)
        print(msg)

    except:
        msg = "Error initialising motion sensor on pin " + str(pin) + "."
        print(msg)
        log_entry(msg)
        sys.exit(2)

    return data, count


def start_ir_sensor(data: dict, pin: int, count: int) -> tuple:
    """Attempts to start the IR sensor.
    Initialises count to 0.
    Returns sensor and data dictionary.
    """
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN)  
        count = 0  # Shows IR sensor is ready. 

        msg = "Initialising IR sensor on pin " + str(pin) + "."
        log_entry(msg)
        print(msg) 

        sleep(10)  # Give sensor time to start.

        msg = "Initialised IR sensor on pin " + str(pin) + "."
        log_entry(msg)
        print(msg)

    except:
        error_msg = "Error initialising IR sensor on pin " + str(pin) + "."
        log_entry(error_msg)
        print(error_msg)
        sys.exit(2)

    return data, count


def save_data(data: dict, count: int) -> tuple:
    """Save the time and count to the dictionary."""
    now = datetime.now().strftime("%H:%M")
    data["timeRecieved"][now] = count
    count = 0
    return data, count


def send_data(data: dict, count: int, col: pymongo.MongoClient, interval: int) -> None:
    """Send sensor data to backend. No return."""
    # Sensor not active.
    if count == -1: return  

    # Append the current time to the data dictionary before sending.
    now = datetime.now().strftime("%d/%m/%Y-%H:%M")
    data["timeSent"] = now

    # Attempt to send the data to the backend.
    try:
        r = col.insert_one(data)
        # Response from the backend.
        log_entry(r)  
        # Reset variables.
        count = 0
        data = {
            "timeSent" : "",
            "timeRecieved" : {}
        }
    except:
        log_entry("Failed logging count of " + str(count) + "Will try again in " + str(interval) + " seconds.")
    return data, count


def log_entry(message: str) -> None:
    """Append a timestamp + message to the dated log file. No return"""
    # Guard clauses.
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
    # argv = ['sensor.py', '-s', 'motion', '-p', '17', '-i', '600']
    main(sys.argv)
