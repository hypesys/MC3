import os
import time
from threading import Thread
import argparse

# taskset -c 1-5 ./build/transmitter copy 6 0 134217728 "UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU" 5 0.5
# Lists of values for transmitter and receiver
# transmitter_values = [134217728, 67108864, 33554432, 16777216, 8388608, 4194304,2097152, 1998848, 1900544, 1802240, 1703936, 1605632, 1507328, 1409024, 1310720, 1212416, 1114112, 1015808, 917504, 819200, 720896, 622592, 524288]
# receiver_values = [8000000]

transmitter_values = [16777216]
receiver_values = [8000000, 4000000, 2000000]
time_switch_list = [0.00] # time_switch_list = [1000,500,250,125,100,50,25,20,10,5,2.5,2,1.333,1.25,1,0.8,0.666,0.5,0.4,0.3,0.25,0.1]
sleep_time_values = [0]

# Function to run receiver
def run_receiver(receiver_size, receiver_iterations, log_dir, transmitter_size, time_switch, sleep_time):
    command = f"taskset -c 0 ~/cuda_samples/1_Utilities/bandwidthTest/bandwidthTest --start={receiver_size} --end={receiver_size} --increment={receiver_size} --mode=range --iteration=100000 > {log_dir}/sleeptime{sleep_time}_time_switch{time_switch}_receiver{receiver_size}_transmitter{transmitter_size}.log"
    print(command)
    os.system(command)

# Function to run transmitter
def run_transmitter(transmitter_size, log_dir, receiver_size, time_switch, sleep_time):
    command = f"taskset -c 1-11 ./build/transmitter copy 0 512 {transmitter_size} 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU' {time_switch} {sleep_time}  > {log_dir}/sleeptime{sleep_time}_time_switch{time_switch}_transmitter{transmitter_size}_receiver{receiver_size}.log"
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
                    if count <= 0:
                        print(count, time_switch)
                        print(transmitter_size, receiver_size)
                        continue
                    # exit()
                    # Calculate the buffer size for the receiver
                    iteration = 80*390000 / 200 * time_switch / 2097152 * transmitter_size

                    # Start the receiver in a separate thread
                    receiver_thread = Thread(target=run_receiver, args=(receiver_size, iteration, args.log_dir, transmitter_size, time_switch, sleep_time))
                    receiver_thread.start()

                    # Wait for 1 second before starting the transmitter
                    # time.sleep(1)

                    # Start the transmitter
                    run_transmitter(transmitter_size, args.log_dir, receiver_size, time_switch, sleep_time)

                    # Wait for the receiver thread to finish before moving to the next iteration
                    receiver_thread.join()

                    # Test for one iteration
                    # time.sleep(1)
                    # exit()

    print("All transmitter and receiver commands have been executed.")
