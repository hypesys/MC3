import os
import time
from threading import Thread
import argparse


#Transfer rate (switch from high to low or vice versa)
time_switch_list = [1000,500,250,125,100,50,25,20,10,5]
receiver_values = [104857600, 52428800, 26214400]


# Function to run receiver
def run_receiver(receiver_size, receiver_iterations, receiver_buffer_size,log_dir,time_switch):
    command = f"./build/receiver copy 0 {receiver_iterations} {receiver_buffer_size} {receiver_size} > {args.log_dir}/time_switch{time_switch}_receiver{receiver_size}_transmitter{transmitter_size}.log"
    os.system(command)

# Function to run transmitter
def run_transmitter(transmitter_size,time_switch,receiver_size,log_dir):
    command = f"taskset -c 0-1 ./build/transmitter copy 0 0 {transmitter_size} 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU' {time_switch} > {log_dir}/time_switch{time_switch}_transmitter{transmitter_size}_receiver{receiver_size}_cores0-1.log"
    os.system(command)



count  = 0 

for receiver_size in receiver_values:
	for time_switch in time_switch_list:
		count += 1
		if count <= 0:
			print(count, time_switch)
			continue
		# Set up command-line argument parsing
		parser = argparse.ArgumentParser(description="Run transmitter and receiver with dynamic log directory.")
		parser.add_argument("--log_dir", type=str, required=True, help="Directory to store the log files for both transmitter and receiver, generally logs/.")

		parser.add_argument("--transmitter_size", type=int, required=True, help="Transmitter buffer size.")
		# parser.add_argument("--receiver_size", type=int, required=True, help="Receiver buffer size.")

		# Parse the command-line arguments
		args = parser.parse_args()

		# Iterate over the lists of values
		transmitter_size = args.transmitter_size
		# receiver_size = args.receiver_size
		# Calculate the buffer size  for the receiver
		buffer_size = 16384 * (1073741824 / receiver_size * time_switch / 1000  )

		# Start the receiver in a separate thread
		receiver_thread = Thread(target=run_receiver, args=(receiver_size, 32, buffer_size, args.log_dir, time_switch))
		receiver_thread.start()

		# Wait for 1 second before starting the transmitter
		time.sleep(1)

		# Start the transmitter
		run_transmitter(transmitter_size,time_switch,receiver_size,args.log_dir)

		# Wait for the receiver thread to finish before moving to the next iteration
		receiver_thread.join()

		# exit()

print("All transmitter and receiver commands have been executed.")