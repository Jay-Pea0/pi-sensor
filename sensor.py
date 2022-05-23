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
    # Mongo setup.
    client = pymongo.MongoClient("mongodb+srv://Pi:6ciXdbklDynHHH5i@vanilla.mfxfp.mongodb.net/?retryWrites=true&w=majority")
    db = client.LoneWorking
    col = db["SensorData"]

    # Other.
    sensor_type, pin, polling_interval = parse_command_line(argv)
    data = {
        "timeSent" : "",
        "timeRecieved" : {}
    }
    count = -1

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
        now_minute_seconds = datetime.now().strftime("%M:%S")
        if now_minute_seconds[1:] == "0:00":
            data = send_data(data, col)

        if sensor_type == "motion":
            if GPIO.input(pin): 
                count += 1
                print("count=" + str(count))
            sleep(polling_interval)

        elif sensor_type == "ir":
            if GPIO.input(pin):
                count += 1
                print("count=" + str(count))
            sleep(polling_interval)

def parse_command_line(argv: list) -> tuple:
    """Get the command line arguments, if any.
    Returns tuple of sensor_type, pin, count.
    """
    # Defaults - can set at command line.
    polling_interval = 1  # If motion, save every 1 minute.
    pin = 17                
    sensor_type = "motion"
    
    if len(argv) == 1: return sensor_type, pin, polling_interval

    # Command line arguments and parsing.
    help_statement = str(argv[0]) + " -s <motion|ir> -p <pin #> -i <polling interval/s>"

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
            polling_interval = arg
            try:
                polling_interval = int(polling_interval)
            except:
                print("Polling Interval must be a whole number.")
                sys.exit()
            if polling_interval < 0:
                print("Polling Interval of " + str(polling_interval) + "is too short.")
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
    msg = "Saving count of " + str(count) + "."
    log_entry(msg)
    print(msg)
    data["timeRecieved"][now] = count
    count = 0
    return data, count


def send_data(data: dict, col: pymongo.MongoClient) -> dict:
    """Send sensor data to backend. Returns data (reset if successful)."""
    empty_dict = {
        "timeSent" : "",
        "timeRecieved" : {}
    }
    if data == empty_dict: return

    # Append the current time to the data dictionary before sending.
    now = datetime.now().strftime("%d/%m/%Y-%H:%M")
    data["timeSent"] = now

    # Attempt to send the data to the backend.
    try:
        col.insert_one(data)
        # Response from the backend.
        msg = "Saved to the database."
        log_entry(msg)
        print(msg)
        return empty_dict
    except:
        msg = "Failed logging to the database. Will try again in 10 minutes."
        log_entry(msg)
        print(msg)
        return data


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
    main(sys.argv)


