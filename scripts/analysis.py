from datetime import datetime
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
    """Parse time string formatted as 'HH:MM:SS:ms:extra' into a datetime object."""
    # Trying to automatically detect and handle the format
    format_str = '%H:%M:%S:%f'
    if len(time_str.split(':')) > 4:  # Indicates extra segments like :415
        format_str += ':%f'
    try:
        return datetime.strptime(time_str, format_str)
    except ValueError as e:
        print(f"Failed to convert time_str={time_str} with error: {e}")
        # Optionally, you can return None or handle it differently
        return None

def merge_files_with_transmitterTiming_and_receiverBW(transmitter_file, receiver_file, output_file):
    with open(transmitter_file, 'r') as t_file, open(receiver_file, 'r') as r_file, open(output_file, 'w') as out_file:
        transmitter_lines = t_file.readlines()
        receiver_lines = r_file.readlines()

        # Ignore the first 32 warmup lines in receiver
        # Define another integer if warmup is different.
        receiver_lines = receiver_lines[32:]

        r_index = 0
        results = []
        total_average_bandwidth = 0
        average_bandwidth_count = 0

        for t_line in transmitter_lines:
            # print("Current t_line: ", t_line)
            # Extract time from the transmitter log line
            t_type, t_time_str = t_line.strip().split()
            t_time = parse_time(t_time_str)

            # Find the closest receiver time that is after the current transmitter time
            while r_index < len(receiver_lines):
                r_line = receiver_lines[r_index].strip()
                match = re.match(r'(\d{2}:\d{2}:\d{2}:\d{3})\s+&\s+(\d+(\.\d+)?)', r_line)
                if match:
                    r_time_str, r_bandwidth_str = match.groups()[0], match.groups()[1]
                    r_time = parse_time(r_time_str)
                    # print("r_time_str: " ,r_time_str)
                    # print("r_time: " ,r_time)

                    if r_time >= t_time:
                        break

                r_index += 1


            # print(" r_index: ",r_index)
            if r_index < len(receiver_lines):
                start_index = r_index

                # Find the next transmitter time to calculate the bandwidth average
                next_t_time = None
                if transmitter_lines.index(t_line) + 1 < len(transmitter_lines):
                    next_t_line = transmitter_lines[transmitter_lines.index(t_line) + 1]
                    next_t_time_str = next_t_line.split()[1]
                    next_t_time = parse_time(next_t_time_str)

                # Find the end index in the receiver log
                end_index = start_index
                while end_index < len(receiver_lines):
                    r_line = receiver_lines[end_index].strip()
                    match = re.match(r'(\d{2}:\d{2}:\d{2}:\d{3})\s+&\s+(\d+(\.\d+)?)', r_line)
                    if match:
                        r_time_str, _ = match.groups()[0], match.groups()[1]
                        r_time = parse_time(r_time_str)

                        if next_t_time and r_time > next_t_time:
                            break

                    end_index += 1
                # print("end index: ",end_index)

                # Calculate the average bandwidth
                total_bandwidth = 0
                count = 0
                for r_bw_line in receiver_lines[start_index:end_index]:
                    match_bw = re.match(r'(\d{2}:\d{2}:\d{2}:\d{3})\s+&\s+(\d+(\.\d+)?)', r_bw_line.strip())
                    if match_bw:
                        _, bw_str = match_bw.groups()[0], match_bw.groups()[1]
                        total_bandwidth += float(bw_str)
                        count += 1

                average_bandwidth = total_bandwidth / count if count > 0 else 0

                total_average_bandwidth += average_bandwidth if average_bandwidth > 0 else 0

                average_bandwidth_count += 1 if average_bandwidth > 0 else 0



                # Write the results to the output file
                out_file.write(f'{t_time_str}, {average_bandwidth:.3f} GB/s\n')

        if average_bandwidth_count > 0:
            Averabe_bandwidth_results_after_experiment = total_average_bandwidth/average_bandwidth_count
        else:
            Averabe_bandwidth_results_after_experiment = 0

        out_file.write(f'Average: {Averabe_bandwidth_results_after_experiment:.3f} GB/s\n')               



transmitter_values = [134217728]#, 536870912, 268435456, 134217728, 67108864, 33554432, 16777216]
receiver_values = [104857600, 52428800, 26214400, 13107200, 6553600, 3276800, 1638400]#, 1433600, 1228800, 1024000, 819200, 716800, 614400, 512000, 409600, 204800]

time_switch_list = [0]
sleep_time_values=[0]


for transmitter_size in transmitter_values:
    for receiver_size in receiver_values:
        for time_switch in time_switch_list:
            for sleep_time in sleep_time_values:

                # transmitter_file = f'{args.log_dir}/transmitter{transmitter_size}_receiver{receiver_size}_cores1,3,5.log'
                # receiver_file = f'{args.log_dir}/receiver{receiver_size}_transmitter{transmitter_size}_cores0,2,4.log'
                # output_file = f'{args.log_dir}/merged_transmitter{transmitter_size}_receiver{receiver_size}_cores0,2,4.log'

                # transfer rate files (encoded as time_switch1000_.....)
                
                transmitter_file = f'{args.log_dir}/transmitter{transmitter_size}_receiver{receiver_size}.log'
                receiver_file = f'{args.log_dir}/receiver{receiver_size}_transmitter{transmitter_size}.log'
                output_file = f'{args.log_dir}/merged_transmitter{transmitter_size}_receiver{receiver_size}.log'

                # transmitter_file = f'{args.log_dir}/transmitterSleep{sleep_time}_time_switch{time_switch}_transmitter{transmitter_size}_receiver{receiver_size}_cores0-3.log'
                # receiver_file = f'{args.log_dir}/transmitterSleep{sleep_time}_time_switch{time_switch}_receiver{receiver_size}_transmitter{transmitter_size}_cores0-3.log'
                # output_file = f'{args.log_dir}/transmitterSleep{sleep_time}_time_switch{time_switch}_merged_transmitter{transmitter_size}_receiver{receiver_size}_cores0-3.log'

                if args.mergeFile:
                    merge_files_with_transmitterTiming_and_receiverBW(transmitter_file, receiver_file, output_file)
                # exit()



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
                    

# Process files
if args.calculateAccuracy == "Average":
    calculate_accuracy_based_on_average(transmitter_values, receiver_values,time_switch_values)


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
        accurate_values = parse_accurate_values_from_file(transmitter_file_content)

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
            # print("i: ", i, " previous_predicted: ",previous_predicted)
            # print("bandwidths[i] ", bandwidths[i])
            # print("bandwidths[i-1] ", bandwidths[i-1])
            # print("percentage_change: ", percentage_change)
            # If the previous prediction was 0 (low)
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
        
        return accuracy, incorrect_indexes, predicted_values




if args.calculateAccuracy == "History":
    
    transmitter_values = [134217728]
    receiver_values = [104857600]
    sleep_time_values = [0.0,0.15]
    time_switch_list = [1000,500,250,200,125,100,50,25,20,10,5,2.5,2,1]


    for transmitter_size in transmitter_values:
        for receiver_size in receiver_values:
            for time_switch in time_switch_list:
                for sleep_time in sleep_time_values:

                    # transmitter_file = f'{args.log_dir}/transmitter{transmitter_size}_receiver{receiver_size}_cores1,3,5.log'
                    # receiver_file = f'{args.log_dir}/receiver{receiver_size}_transmitter{transmitter_size}_cores0,2,4.log'
                    # output_file = f'{args.log_dir}/merged_transmitter{transmitter_size}_receiver{receiver_size}_cores0,2,4.log'
                    # print(output_file)

                    # An error in one of the logs, ignore for now.
                    # if "logs_1024_iteration/merged_transmitter67108864_receiver512000.log" in output_file:
                    #     print("")
                    #     continue
                    
                    # transfer rate files (encoded as time_switch1000_.....)
                
                    # transmitter_file = f'{args.log_dir}/time_switch{time_switch}_transmitter{transmitter_size}_receiver{receiver_size}_cores0-3.log'
                    # receiver_file = f'{args.log_dir}/time_switch{time_switch}_receiver{receiver_size}_transmitter{transmitter_size}_cores4-5.log'
                    # output_file = f'{args.log_dir}/time_switch{time_switch}_merged_transmitter{transmitter_size}_receiver{receiver_size}_cores4-5.log'
                    # print(output_file)


                    transmitter_file = f'{args.log_dir}/transmitterSleep{sleep_time}_time_switch{time_switch}_transmitter{transmitter_size}_receiver{receiver_size}_cores0-3.log'
                    receiver_file = f'{args.log_dir}/transmitterSleep{sleep_time}_time_switch{time_switch}_receiver{receiver_size}_transmitter{transmitter_size}_cores0-3.log'
                    output_file = f'{args.log_dir}/transmitterSleep{sleep_time}_time_switch{time_switch}_merged_transmitter{transmitter_size}_receiver{receiver_size}_cores0-3.log'# print(output_file)

                    # Calculate the accuracy and mispredicted indexes
                    overall_accuracy, mispredicted_indexes, predicted_values = calculate_threshold_accuracy(transmitter_size, receiver_size,output_file,time_switch, args.threshold)

                    # Print the results
                    
                    if overall_accuracy < 50:
                        print(f"{sleep_time} {time_switch} {transmitter_size} {receiver_size} {100-overall_accuracy:.2f}%")
                        print(f" Overall accuracy: {100-overall_accuracy:.2f}%")
                    else:
                        print(f"{sleep_time} {time_switch} {transmitter_size} {receiver_size} {overall_accuracy:.2f}%")
                        print(f" Overall accuracy:  {overall_accuracy:.2f}%")
                    
                    # print(f"{sleep_time} {1000/time_switch:.0f} {overall_accuracy:.2f}%")
                    # print(f"Mispredicted Indexes: {mispredicted_indexes}")
                    # print(f"Predicted Values: {predicted_values}")
                    # exit()