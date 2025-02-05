from datetime import datetime

def parse_timestamp(timestamp_str):
    # Split the string by space and get the time part after "Low" or "High"
    _, timestamp = timestamp_str.split(' ')
    
    # Extract hours, minutes, seconds, milliseconds, and microseconds manually
    hours = timestamp[:2]
    minutes = timestamp[3:5]
    seconds = timestamp[6:8]
    milliseconds = timestamp[9:12]
    microseconds = timestamp[13:]
    
    # Ensure microseconds are exactly 3 digits
    if len(microseconds) > 3:
        microseconds = microseconds[:3]  # Truncate if longer
    microseconds = microseconds.ljust(3, '0')  # Pad to ensure it's 3 digits
    
    # Combine milliseconds and microseconds into a 6-digit number
    full_microseconds = milliseconds + microseconds
    
    # Combine into a string that the datetime parser can understand
    reformatted_timestamp = f"{hours}:{minutes}:{seconds}.{full_microseconds}"
    
    # Parse the reformatted timestamp into a datetime object
    return datetime.strptime(reformatted_timestamp, "%H:%M:%S.%f")

def calculate_time_difference(merged_file):
    with open(merged_file, 'r') as file:
        # Read the content of the file
        file_content = file.readlines()
        
        # Get first and last timestamp
        first_value = file_content[0].strip()  # Ensure no newline characters
        last_value = file_content[-1].strip()  # Ensure no newline characters

        # print(first_value)
        # print(last_value)
        
        # Parse both timestamps
        first_time = parse_timestamp(first_value)
        last_time = parse_timestamp(last_value)
        
        # Calculate the difference in time
        time_difference = last_time - first_time
    
    # Convert time difference to milliseconds
    time_diff_ms = time_difference.total_seconds() * 1000
    # print("time diff: ", time_diff_ms)
    # print("len(file_content) * 2 / 3", len(file_content) * 2 / 3)
    avg_transmit_time = len(file_content) * 2 / 3 / time_diff_ms * 1000
    # print("avg_transmit_time",avg_transmit_time)
    
    return time_diff_ms, avg_transmit_time


# Example usage with file processing
transmitter_values = [134217728, 67108864, 33554432, 16777216, 8388608, 4194304,2097152, 1998848, 1900544, 1802240, 1703936, 1605632, 1507328, 1409024, 1310720, 1212416, 1114112, 1015808, 917504, 819200, 720896, 622592, 524288]
receiver_values = [104857600, 13107200, 1024000]
for rec in receiver_values:
    for tran in transmitter_values:

        #cpu to gpu
        merged_file = f"logs/transmitter_rate_by_buffer_size/sleeptime0_time_switch0.0_transmitter{tran}_receiver{rec}.log"
        standalone_file = f"logs/transmitter_rate_by_buffer_size/sleeptime0_time_switch0.0_transmitter{tran}_receiver8000000_2ndversion.log"
                        # logs/transmitter_rate_by_buffer_size/sleeptime0_time_switch0.0_transmitter134217728_receiver8000000.log
        

        #only cpu files
        merged_file = f"logs/transmitter_rate_by_buffer_size_cpu_to_cpu/transmitter{tran}_receiver{rec}_cores0-2.log"
        standalone_file = f"logs/transmitter_rate_by_buffer_size_cpu_to_cpu/transmitter{tran}_receiver{rec}_cores_standalone.log"
                        # logs/transmitter_rate_by_buffer_size/sleeptime0_time_switch0.0_transmitter134217728_receiver8000000.log
        

        # Call the function to process the file content
        time_difference, average_transmit = calculate_time_difference(merged_file)
        time_difference2, average_transmit_standalone = calculate_time_difference(standalone_file)
        
        
        print(rec, tran, average_transmit)
        # print(average_transmit)
        # print(average_transmit_standalone)
    print()
        # exit()