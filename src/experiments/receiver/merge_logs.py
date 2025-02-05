def merge_logs(transmitter_num, receiver_num):
    for i in range(1, transmitter_num + 1):
        # Define file names
        transmitter_file = f'transmitter{i}.log'
        receiver_file = f'receiver{i}.log'
        output_file = f'transmitter{i}_receiver{i}.log'
        
        # Open files
        with open(transmitter_file, 'r') as t_file, open(receiver_file, 'r') as r_file, open(output_file, 'w') as out_file:
            # Read lines from both files
            transmitter_lines = t_file.readlines()
            receiver_lines = r_file.readlines()
            
            # Get the max length to ensure all lines are processed
            max_len = max(len(transmitter_lines), len(receiver_lines))
            
            for j in range(max_len):
                if j < len(transmitter_lines):
                    out_file.write(transmitter_lines[j])
                out_file.write("\n")  # Empty line to indicate switch
                if j < len(receiver_lines):
                    out_file.write(receiver_lines[j])
                    
    print(f"Merged logs created for {transmitter_num} files.")

# Example usage:
merge_logs(transmitter_num=3, receiver_num=3)