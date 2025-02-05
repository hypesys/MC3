import numpy as np
import re
import argparse

# Function to add Gaussian noise to data
def add_gaussian_noise(data, noise_percentage):
    noise_std = (noise_percentage / 100) * np.mean(data)
    noise = np.random.normal(0, noise_std, data.shape)
    return data + noise


parser = argparse.ArgumentParser(description="Run transmitter and receiver with dynamic log directory.")
parser.add_argument("--log_dir", type=str, required=True, help="Directory to store the log files for both transmitter and receiver, generally logs/.")

# Parse the command-line arguments
args = parser.parse_args()

transmitter_values = [16777216]#, 536870912, 268435456, 134217728, 67108864, 33554432, 16777216]
receiver_values = [32000000, 16000000]
time_switch_list = [8,4,2,1,0.5,0.25]
noise_percentage_values = [1,2,4,5,8,10,15,20,25,30,40,50]

for transmitter_size in transmitter_values:
    for receiver_size in receiver_values:
        for time_switch in time_switch_list:
            for noise_percentage in noise_percentage_values:

                # File paths
                input_file = f"{args.log_dir}/merged_time_switch{time_switch}_transmitter{transmitter_size}_receiver{receiver_size}.log"
                output_file = f"{args.log_dir}/merged_time_switch{time_switch}_transmitter{transmitter_size}_receiver{receiver_size}_noise{noise_percentage}.log"

                # Read and process data from input file
                with open(input_file, "r") as file:
                    content = file.read()

                # Extract values from the file content using regex to match the pattern
                values = np.array([float(x) for x in re.findall(r", ([\d.]+) ms", content)])

                # Add Gaussian noise to the extracted values
                values_noisy = add_gaussian_noise(values, noise_percentage)

                # Prepare new content with noisy values
                lines = re.findall(r"(.*?, [\d.]+ ms)", content)  # capture entire line format
                noisy_content = "\n".join(
                    f"{line.split(',')[0]}, {noisy_value:.6f} ms"
                    for line, noisy_value in zip(lines, values_noisy)
                )

                # Write the noisy data to the output file
                with open(output_file, "w") as file:
                    file.write(noisy_content)

                print(f"Noisy data written to {output_file}")
