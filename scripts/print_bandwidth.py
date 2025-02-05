def process_file_lines(file_content):
    processed_values = []
    count = 0
    for line in file_content:
        # Split by comma and take the part after the comma
        count += 1
        # print (line)
        if count < 0:
            continue
        if "Device to Device Bandwidth" in line:
            return processed_values
        parts = line.split(',')
        if count % 2 == 0:
            
            if len(parts) > 1:
                print(parts[1].strip())
            # processed_values.append(value)
    
    return processed_values



transmitter_values = [1073741824, 536870912, 268435456, 134217728, 67108864, 33554432, 16777216]
# transmitter_values = [134217728] #one sample test
receiver_values = [13107200]
# receiver_values = [104857600, 52428800, 26214400, 13107200, 6553600, 3276800, 1638400, 1433600, 1228800, 1024000, 819200, 716800, 614400, 512000, 409600, 204800]
# receiver_values = [1024000] #one sample test
transmitter_values = [1048576]
receiver_values = [16000000,8000000,4000000,2000000,1000000,500000] #100000
time_switch_values = [500]
transmitter_values = [4194304]
receiver_values = [26214400, 13107200, 6553600, 3276800, 1638400, 1433600, 1228800, 1024000, 819200, 716800]

time_switch_list = [1]
sleep_time_values=[0]
# time_switch_values = [1000,500,250,125,100,50,25,20,10,5,2,1]

for transmitter_size in transmitter_values:
        for receiver_size in receiver_values:
            
            print ("Transmitter: ",transmitter_size ) 
            print ("Receiver: ",receiver_size ) 
            merged_file = f'logs/cpu_cpu_receiver_size_distribution/time_switch10_merged_transmitter{transmitter_size}_receiver{receiver_size}_cores0-2.log'
            # print (merged_file)
            # print("merged_file: ",merged_file)
            with open(merged_file, 'r') as file:
                lines = file.readlines()

                # Process the file and extract the values
                processed_values = process_file_lines(lines)
                # print(processed_values)

