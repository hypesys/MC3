import os
import time
from threading import Thread
import argparse

# Lists of values for transmitter and receiver
transmitter_values = [134217728]#, 536870912, 268435456, 134217728, 67108864, 33554432, 16777216]
receiver_values = [104857600, 52428800, 26214400, 13107200, 6553600, 3276800, 1638400]#, 1433600, 1228800, 1024000, 819200, 716800, 614400, 512000, 409600, 204800]

# Function to run receiver
def run_receiver(receiver_size, receiver_iterations, receiver_buffer_size, log_dir, transmitter_size):
    command = f"taskset -c 0-3 ./build/receiver copy 0 {receiver_iterations} {receiver_buffer_size} {receiver_size} > {log_dir}/receiver{receiver_size}_transmitter{transmitter_size}.log"
    os.system(command)

# Function to run transmitter
def run_transmitter(transmitter_size, log_dir, receiver_size):
    command = f"taskset -c 4-7 ./build/transmitter copy 0 0 {transmitter_size} 'UUUU' 500 0 > {log_dir}/transmitter{transmitter_size}_receiver{receiver_size}.log"
    os.system(command)

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Run transmitter and receiver with dynamic log directory.")
    parser.add_argument("--log_dir", type=str, required=True, help="Directory to store the log files for both transmitter and receiver, generally logs/.")
    
    # Parse the command-line arguments
    args = parser.parse_args()

    count  = 0 
    # Iterate over the lists of values
    for transmitter_size in transmitter_values:
        for receiver_size in receiver_values:

            print("Receiver size:", receiver_size)
            count += 1
            #If you cut down the experiment, skip the first X experiment. For 0, it won't skip everything and performs every exp.
            if count <= 0:
                continue
            # Calculate the buffer size for the receiver
            buffer_size = 450 * (1073741824 // receiver_size) * (transmitter_size/134217728)

            # Start the receiver in a separate thread
            receiver_thread = Thread(target=run_receiver, args=(receiver_size, 32, buffer_size, args.log_dir, transmitter_size))
            receiver_thread.start()

            # Wait for 1 second before starting the transmitter
            time.sleep(1)

            # Start the transmitter
            run_transmitter(transmitter_size, args.log_dir, receiver_size)

            # Wait for the receiver thread to finish before moving to the next iteration
            receiver_thread.join()

            # Test for one iteration
            # exit()

    print("All transmitter and receiver commands have been executed.")
