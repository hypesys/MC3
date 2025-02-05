import os
import time
from threading import Thread
import argparse

# Lists of values for transmitter and receiver
transmitter_values = [134217728,67108864, 16777216]
receiver_values = [13107200, 3276800, 1024000,409600]
sleep_time_values = [0.0,0.025,0.05,0.075,0.1,0.15,0.2,0.25,0.3]
time_switch_list = [2.5,2,1.6,1.3,1] # time_switch_list = [250,125,100,50,25,20,10,5,2.5,2,1.6,1.3,1]



# transmitter_values = [ 16777216]
# receiver_values = [  1024000]
# sleep_time_values = [0.1]
# time_switch_list = [10]


# Function to run receiver
def run_receiver(receiver_size, receiver_iterations, receiver_buffer_size, log_dir, transmitter_size, time_switch, sleep_time):
    command = f"./build/receiver copy 0 {receiver_iterations} {receiver_buffer_size} {receiver_size} > {log_dir}/transmitterSleep{sleep_time}_time_switch{time_switch}_receiver{receiver_size}_transmitter{transmitter_size}.log"
    os.system(command)

# Function to run transmitter
def run_transmitter(transmitter_size, log_dir, receiver_size, time_switch, sleep_time):
    command = f"./build/transmitter copy 0 0 {transmitter_size} 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU' {time_switch} {sleep_time} > {log_dir}/transmitterSleep{sleep_time}_time_switch{time_switch}_transmitter{transmitter_size}_receiver{receiver_size}.log"
    os.system(command)

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Run transmitter and receiver with dynamic log directory.")
    parser.add_argument("--log_dir", type=str, required=True, help="Directory to store the log files for both transmitter and receiver, generally logs/.")
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Iterate over the lists of values
    for transmitter_size in transmitter_values:
        for receiver_size in receiver_values:
            for time_switch in time_switch_list:
                for sleep_time in sleep_time_values:
                    # Calculate the buffer size for the receiver
                    buffer_size = 60 * (1073741824 / receiver_size)* (time_switch / 15)

                    # Start the receiver in a separate thread
                    receiver_thread = Thread(target=run_receiver, args=(receiver_size, 32, buffer_size, args.log_dir, transmitter_size, time_switch, sleep_time))
                    receiver_thread.start()

                    # Wait for 1 second before starting the transmitter
                    time.sleep(1)

                    # Start the transmitter
                    run_transmitter(transmitter_size, args.log_dir, receiver_size, time_switch, sleep_time)

                    # Wait for the receiver thread to finish before moving to the next iteration
                    receiver_thread.join()

                    # Test for one iteration
                    # exit()

    print("All transmitter and receiver commands have been executed.")
