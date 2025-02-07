from datetime import datetime, timedelta
import re
import argparse

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="Run transmitter and receiver with dynamic log directory.")
parser.add_argument("--log_dir", type=str, required=True, help="Directory to store the log files for transmitter and receiver.")
parser.add_argument("--mergeFile", type=lambda x: (str(x).lower() == 'true'), default=True, help="Set to True or False. Default is True.")
# parser.add_argument("--iteration_count", type=int, required=True, help="Number of iterations for how many bits are transmitted.")
parser.add_argument("--calculateAccuracy", type=str, required=True, help="Mode for calculating accuracy (e.g., Average, History, etc.).")
parser.add_argument("--threshold", type=float, default=0.30, help="Threshold for percentage increase or decrease.")



# Parse the command-line arguments
args = parser.parse_args()

def parse_time(time_str):
    """Parse time string formatted as 'HH:MM:SS:xxx:yyy' (milliseconds and microseconds)."""
    time_parts = time_str.split(':')

    if len(time_parts) != 5:
        raise ValueError(f"Time string '{time_str}' is not in the expected format 'HH:MM:SS:xxx:yyy'")

    # Extract hours, minutes, seconds, milliseconds, microseconds
    hours = time_parts[0]
    minutes = time_parts[1]
    seconds = time_parts[2]
    milliseconds = time_parts[3]
    microseconds = time_parts[4]

    # Combine milliseconds and microseconds into a single microsecond value
    combined_microseconds = int(milliseconds) * 1000 + int(microseconds)

    # Create a datetime object with the combined time information
    return datetime.strptime(f"{hours}:{minutes}:{seconds}", '%H:%M:%S') + timedelta(microseconds=combined_microseconds)


def merge_files_with_transmitterTiming_and_receiverBW(transmitter_file, receiver_file, output_file):
    with open(transmitter_file, 'r') as t_file, open(receiver_file, 'r') as r_file, open(output_file, 'w') as out_file:
        transmitter_lines = t_file.readlines()
        receiver_lines = r_file.readlines()

        # Ignore the first 32 warmup lines in receiver
        receiver_lines = receiver_lines[34:]

        r_index = 0

        for t_index in range(0, len(transmitter_lines) - 1):
            if "Transmitter runs" in transmitter_lines[t_index]:
                continue
            # Process both "Low" and "High" transmitter lines
            t_type, t_time_str = transmitter_lines[t_index].strip().split()

            # Get the next transmitter line (whether Low or High) to mark the range
            t_next_type, t_next_time_str = transmitter_lines[t_index + 1].strip().split()

            t_start_time = parse_time(t_time_str)
            t_end_time = parse_time(t_next_time_str)

            # Collect all receiver bandwidth values between the current and next transmitter times
            bandwidth_sum = 0
            receiver_count = 0

            

            while r_index < len(receiver_lines):
                if "Device to Device" in receiver_lines[r_index]:
                    return
                  
                r_line = receiver_lines[r_index].strip()
                r_time_str, _, r_bw_str = r_line.split()  # Split by spaces
                r_time = parse_time(r_time_str)

                # Check if receiver time is within the transmitter time range
                if t_start_time <= r_time <= t_end_time:
                    r_bw = float(r_bw_str)  # Convert bandwidth string to float
                    bandwidth_sum += r_bw
                    receiver_count += 1
                elif r_time > t_end_time:
                    break

                r_index += 1

            if receiver_count > 0:
                # Calculate the average bandwidth
                average_bandwidth = bandwidth_sum / receiver_count

                # Write the result to the output file in GB/s
                # out_file.write(f"{t_type} {t_time_str} to {t_next_type} {t_next_time_str}: Average Bandwidth = {average_bandwidth:.6f} GB/s\n")

                # Write the result to the output file in GB/s
                out_file.write(f"{t_time_str}, {average_bandwidth:.6f} ms\n")


        



def parse_timestamp(timestamp_str):
    # Split the timestamp string to separate the time and the throughput value
    timestamp, _ = timestamp_str.split(', ')
    
    # Reformat the timestamp string to separate milliseconds and microseconds
    # '21:51:39:871:009' becomes '21:51:39.871009'
    reformatted_timestamp = timestamp[:8] + '.' + timestamp[9:12] + timestamp[13:]
    
    # Parse the reformatted timestamp into a datetime object with microseconds
    return datetime.strptime(reformatted_timestamp, "%H:%M:%S.%f")

def calculate_time_difference(merged_file):


    with open(merged_file, 'r') as file:
        
        file_content = file.readlines()
        
        if len(file_content) < 1:
            return 0,0

        # Read the content of the file
        first_value=file_content[0]

        last_value=file_content[-1]
        first_time = parse_timestamp(first_value)
        last_time = parse_timestamp(last_value)
        
        # Calculate the difference in time
        time_difference = last_time - first_time
    
    # Convert time difference to milliseconds
    return time_difference.total_seconds() * 1000,time_difference.total_seconds() * 1000/len(file_content)





def calculate_accuracy_based_on_average(transmitter_values, receiver_values,time_switch_values):

    for transmitter_size in transmitter_values:
        for receiver_size in receiver_values:
            for time_switch in time_switch_values:
                merged_file = f'{args.log_dir}/merged_transmitter{transmitter_size}_receiver{receiver_size}.log'
                # print("merged_file: ",merged_file)
                with open(merged_file, 'r') as file:
                    lines = file.readlines()
                    
                    # print("lines: ", lines)
                    # Parse bandwidth values and the average
                    bandwidths = []
                    for line in lines[:len(lines)]:
                        # print("line: ", line)
                        # Split by comma to separate time from bandwidth
                        parts = line.split(',')
                        # Extract the bandwidth part and convert to float
                        bandwidth = float(parts[1].split()[0])  # Extract the first part and convert to float
                        bandwidths.append(bandwidth)
                    
                    # Extract the average bandwidth from the 33rd line
                    average_bandwidth = float(lines[len(lines)].split()[-2])  # Assuming "Average" is followed by the value

                    # Determine the expected high-low pattern
                    expected_pattern = []
                    for i in range(len(lines)):
                        if i % 2 == 0:
                            expected_pattern.append(bandwidths[i] < average_bandwidth)
                        else:
                            expected_pattern.append(bandwidths[i] > average_bandwidth)
                    
                    # Calculate accuracy
                    accuracy = sum(expected_pattern) / len(lines) * 100.0
                    
                    # Print the accuracy
                    print(f"Accuracy for {transmitter_size} and {receiver_size}: {accuracy:.2f}%")
                    


def parse_accurate_values_from_file(file_content):
    accurate_values = []
    for line in file_content:
        if "Low" in line:
            accurate_values.append(0)
        elif "High" in line:
            accurate_values.append(1)
    return accurate_values


def calculate_threshold_accuracy(transmitter_size, receiver_size, output_file, time_switch, threshold):

   
    with open(output_file, 'r') as file, open(transmitter_file, 'r') as t_file:
        
        #Merged file
        lines = file.readlines()
        # Parse bandwidth values and the average
        bandwidths = []
        
        #transmitter file accurate values (Transmitted message as baseline)
        transmitter_file_content = t_file.readlines()
        accurate_values = parse_accurate_values_from_file(transmitter_file_content[1:])

        for line in lines[:len(lines)-1]:
            # print("line: ", line)
            # Split by comma to separate time from bandwidth
            parts = line.split(',')
            # Extract the bandwidth part and convert to float
            bandwidth = float(parts[1].split()[0])  # Extract the first part and convert to float
            bandwidths.append(bandwidth)

        predicted_values = []
        correct_predictions = 0
        incorrect_indexes = []
        # Initialize with the first value from the accurate values
        predicted_values.append(accurate_values[0])
        
        for i in range(1, len(bandwidths)):
            previous_predicted = predicted_values[-1]
            # print("bandwidths[i - 1]: ", bandwidths[i - 1])
            if bandwidths[i - 1] > 0:
                percentage_change = (bandwidths[i] - bandwidths[i - 1]) / bandwidths[i - 1]
            elif bandwidths[i - 1] == 0:
                percentage_change = 100
            if previous_predicted == 0:
                if percentage_change >= threshold:
                    predicted_values.append(1)  # Mark as high
                else:
                    predicted_values.append(0)  # Stay low
            # If the previous prediction was 1 (high)
            else:
                if percentage_change <= -threshold:
                    predicted_values.append(0)  # Mark as low
                else:
                    predicted_values.append(1)  # Stay high
            
            # Compare the predicted value with the accurate value
            if predicted_values[-1] == accurate_values[i]:
                correct_predictions += 1
            else:
                incorrect_indexes.append(i)
                # print("incorrect i: ", i)
        
        total_predictions = len(bandwidths)-1
        accuracy = (correct_predictions / total_predictions) * 100
        
        return accuracy, incorrect_indexes, predicted_values, len(lines)






#Buffer size of transmitter
transmitter_values = [16777216] #536870912, 268435456, 134217728, 67108864, 33554432, 16777216, 8388608, 4194304,2097152, 

#Buffer size of receiver
receiver_values = [32000000] #64000000, 32000000, 16000000, 8000000, 4000000, 2000000

# Time spent to switch from 0 to 1 or vice versa. This is an ideal channel capacity/channel bandwidth.
time_switch_list = [50] # time_switch_list = [1000,500,250,125,100,50,25,16,8,4,2,1,0.5,0.25]

#This value can stay as 0 for this experiment. This is early finish while creating contention (sleep ratio). Alternative rates are given in the comments
sleep_time_values = [0] # 0,0.025,0.05,0.075,0.1,0.15,0.2,0.25,0.3


count = 0

for transmitter_size in transmitter_values:
    for receiver_size in receiver_values:
        for time_switch in time_switch_list:
            for sleep_time in sleep_time_values:
                count += 1
                if count < 0:
                    continue
                

                
                transmitter_file = f'{args.log_dir}/time_switch{time_switch}_transmitter{transmitter_size}_receiver{receiver_size}.log'
                receiver_file = f'{args.log_dir}/time_switch{time_switch}_receiver{receiver_size}_transmitter{transmitter_size}.log'
                output_file = f'{args.log_dir}/merged_time_switch{time_switch}_transmitter{transmitter_size}_receiver{receiver_size}.log'

                
                # output_file = f'{args.log_dir}/merged_time_switch{time_switch}_transmitter{transmitter_size}_receiver{receiver_size}_noise{noise_percentage}.log'


                
            

                if args.mergeFile:
                    print(output_file)
                    merge_files_with_transmitterTiming_and_receiverBW(transmitter_file, receiver_file, output_file)

                # Process files
                if args.calculateAccuracy == "Average":
                    calculate_accuracy_based_on_average(transmitter_values, receiver_values, time_switch_list)

                if args.calculateAccuracy == "History":

                    # Calculate the accuracy and mispredicted indexes
                    overall_accuracy, mispredicted_indexes, predicted_values,number_of_sample = calculate_threshold_accuracy(transmitter_size, receiver_size,output_file,time_switch, args.threshold)
                    
                    time_difference,average_transmit = calculate_time_difference(output_file)

                    #Print the result
                    # print(f"{count} {average_transmit} {number_of_sample} {sleep_time} {time_switch} {transmitter_size} {receiver_size} {overall_accuracy:.2f}%")
                    print(f" {overall_accuracy:.2f}%")
                    
                    #Comment out to print Mispredicted indexes
                    print(f"Mispredicted Indexes: {mispredicted_indexes}")
                    # print(f"Predicted Values: {predicted_values}")
                    # exit()
                # exit()