# Pi Sensor

CMP2804M Team Software Engineering (Assessment 3), Achieved 70%

Originally created 2022

Sensor Data from Raspberry Pi

Stores a count of how many times a sensor is activated and sends it to a backend every ten minutes.
The status and count is printed to the console and major events are logged to a log file.

If this was to actually be deployed then the key would need to be stored as a secret and locally (not stored on Github).

cmd line: "<file name> -s <motion|ir> -p <pin #> -i <polling interval/s>"
