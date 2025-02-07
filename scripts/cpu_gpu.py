import os
import time
from threading import Thread
import argparse


#Buffer size of transmitter
transmitter_values = [16777216] #536870912, 268435456, 134217728, 67108864, 33554432, 16777216, 8388608, 4194304,2097152, 

#Buffer size of receiver
receiver_values = [32000000] #64000000, 32000000, 16000000, 8000000, 4000000, 2000000

# Time spent to switch from 0 to 1 or vice versa. This is an ideal channel capacity/channel bandwidth.
time_switch_list = [10] # time_switch_list = [1000,500,250,125,100,50,25,16,8,4,2,1,0.5,0.25]

#This value can stay as 0. This is early finish while creating contention (sleep ratio)
sleep_time_values = [0]

# Function to run receiver
def run_receiver(receiver_size, receiver_iterations, log_dir, transmitter_size, time_switch, sleep_time):
    command = f"taskset -c 0 ~/cuda_samples/1_Utilities/bandwidthTest/bandwidthTest --start={receiver_size} --end={receiver_size} --increment={receiver_size} --mode=range --iteration=100000 > {log_dir}/time_switch{time_switch}_receiver{receiver_size}_transmitter{transmitter_size}.log"
    print(command)
    os.system(command)

# Function to run transmitter. U data represent bit 01010101. So, for each U letter transmitter, we transmit switching 0s and 1s repetitively. Transmitter message can be updated to any message. Note that the analysis script might need an update if the conveyed message is modified.
def run_transmitter(transmitter_size, log_dir, receiver_size, time_switch, sleep_time):
    command = f"taskset -c 1-11 ./build/transmitter copy 0 512 {transmitter_size} 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU' {time_switch} {sleep_time}  > {log_dir}/time_switch{time_switch}_transmitter{transmitter_size}_receiver{receiver_size}.log"
    print(command)
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
            for time_switch in time_switch_list:
                for sleep_time in sleep_time_values:

                    count += 1

                    # Calculate the buffer size for the receiver
                    iteration = 80*390000 / 200 * time_switch / 2097152 * transmitter_size

                    # Start the receiver in a separate thread
                    receiver_thread = Thread(target=run_receiver, args=(receiver_size, iteration, args.log_dir, transmitter_size, time_switch, sleep_time))
                    receiver_thread.start()


                    # Start the transmitter
                    run_transmitter(transmitter_size, args.log_dir, receiver_size, time_switch, sleep_time)

                    # Wait for the receiver thread to finish before moving to the next iteration
                    receiver_thread.join()

                    # Test for one iteration
                    # exit()

    print("All transmitter and receiver commands have been executed.")
