from datetime import datetime

def parse_transmitter_times(transmitter_file):
    with open(transmitter_file, 'r') as file:
        lines = file.readlines()
        
        # Extract start and end times (ignoring milliseconds)
        start_time_str = lines[0].split()[1].rsplit(':', 1)[0]  # Remove milliseconds
        end_time_str = lines[-1].split()[1].rsplit(':', 1)[0]  # Remove milliseconds
        
        start_time = datetime.strptime(start_time_str, '%H:%M:%S')
        end_time = datetime.strptime(end_time_str, '%H:%M:%S')
        
        return start_time, end_time

def find_max_emc_value(emc_file, start_time, end_time):
    max_emc_value = 0
    
    with open(emc_file, 'r') as file:
        for line in file:
            # Extract the time part of the line
            line_time_str = line.split()[1]
            line_time = datetime.strptime(line_time_str, '%H:%M:%S')
            
            # Check if the time is within the start and end time
            if start_time <= line_time <= end_time:
                # Extract the EMC_FREQ value
                if "EMC_FREQ" in line:
                    emc_freq_str = line.split("EMC_FREQ")[1].split('%')[0].split()[-1]
                    emc_value = int(emc_freq_str)
                    max_emc_value = max(max_emc_value, emc_value)
    
    return max_emc_value

def find_average_emc_value(emc_file, start_time, end_time):
    sum_emc_value = 0
    count = 0
    
    with open(emc_file, 'r') as file:
        for line in file:
            # Extract the time part of the line
            line_time_str = line.split()[1]
            line_time = datetime.strptime(line_time_str, '%H:%M:%S')
            
            # Check if the time is within the start and end time
            if start_time <= line_time <= end_time:
                # Extract the EMC_FREQ value
                if "EMC_FREQ" in line:
                    emc_freq_str = line.split("EMC_FREQ")[1].split('%')[0].split()[-1]
                    emc_value = int(emc_freq_str)
                    sum_emc_value += emc_value
                    count += 1
    
    # Calculate the average
    if count > 0:
        average_emc_value = sum_emc_value / count
    else:
        average_emc_value = 0  # Handle the case where no values were found

    return average_emc_value

def main():
    # Specify file names
    transmitter_values = [1073741824, 536870912, 268435456, 134217728, 67108864, 33554432, 16777216]
    receiver_values = [104857600, 52428800, 26214400, 13107200, 6553600, 3276800, 1638400, 1433600, 1228800, 1024000, 819200, 716800, 614400, 512000, 409600, 204800]

    for transmitter_size in transmitter_values:
	    for receiver_size in receiver_values:
		    transmitter_file = f'logs/transmitter{transmitter_size}_receiver{receiver_size}.log'
		    emc_file = 'logs/buffer_size_experiments_tegrastats.log'
		    
		    # Parse transmitter times
		    start_time, end_time = parse_transmitter_times(transmitter_file)
		    
		    # # Find the maximum EMC value within the time range
		    # max_emc_value = find_max_emc_value(emc_file, start_time, end_time)

		    # Find the maximum EMC value within the time range
		    average_emc_value = find_average_emc_value(emc_file, start_time, end_time)

		    # print(transmitter_file)
		    print(f"Average EMC Value between {transmitter_size} and {receiver_size}: {average_emc_value}%") # This can be modified with max_emc_value or average_emc_value
		    # exit()

if __name__ == "__main__":
    main()