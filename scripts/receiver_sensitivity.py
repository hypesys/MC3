import os
import time
from threading import Thread
import argparse


# Lists of values for transmitter and receiver
transmitter_values = [2097152] #2097152
receiver_values = [500000,1000000,2000000,4000000,8000000]
time_switch_list = [1] # time_switch_list = [1000,500,250,125,100,50,25,20,10,5,2.5,2,1.6,1.3,1]
sleep_time_values = [0]

# transmitter_values = [ 16777216]
# receiver_values = [  1024000]
# sleep_time_values = [0.0,0.15,0.25]
# time_switch_list = [10]


# Function to run receiver
def run_receiver_gpu(receiver_size, receiver_iterations, log_dir, transmitter_size, time_switch, sleep_time):
    command = f"taskset -c 0 /home/orinnano/cuda_samples/1_Utilities/bandwidthTest/bandwidthTest --start={receiver_size} --end={receiver_size} --increment={receiver_size} --mode=range --iteration={iteration} > {log_dir}/gpu_time_switch{time_switch}_receiver{receiver_size}_transmitter{transmitter_size}.log"
    os.system(command)

def run_receiver_cpu(receiver_size, receiver_iterations,receiver_buffer_size, log_dir, transmitter_size, time_switch, sleep_time):
    command = f"taskset -c 0-2 ./build/receiver copy 0 {receiver_iterations} {receiver_buffer_size} {receiver_size} > {log_dir}/cpu_transmitterSleep{sleep_time}_time_switch{time_switch}_receiver{receiver_size}_transmitter{transmitter_size}_cores2-5.log"
    print("Command: ", command)
    os.system(command)

# Function to run transmitter
def run_transmitter(transmitter_size, log_dir, receiver_size, time_switch, sleep_time):
    command = f"taskset -c 3-5 ./build/transmitter copy 0 0 {transmitter_size} 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU' {time_switch} 0.0 > {log_dir}/time_switch{time_switch}_transmitter{transmitter_size}_receiver{receiver_size}_cores6-11.log"
    print("Command: ", command)
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
                    iteration = 30000


                    # Start the receiver in a separate thread
                    receiver_thread = Thread(target=run_receiver_gpu, args=(receiver_size, iteration, args.log_dir, transmitter_size, time_switch, sleep_time))
                    # receiver_thread = Thread(target=run_receiver_gpu, args=(receiver_size, 32, iteration, args.log_dir, transmitter_size, time_switch, sleep_time))

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
