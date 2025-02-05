# Covert Channel

## Documentation

### Structure

- `apps/`: example Android applications (Note that these use a separate CMake build system)
  - `Simple-Contacts`: modified [Simple-Contacts](https://github.com/SimpleMobileTools/Simple-Contacts) application
  - `Simple-Notes`: modified [Simple-Notes](https://github.com/SimpleMobileTools/Simple-Notes) application
- `src/`: source code (Uses the top-level CMake build system)
  - `experiments/`: standalone experiments
    - `receiver`: receiver application
      - `main.cpp` receiver application entry point
    - `timing-consistency`: timing consistency benchmark
      - `main.cpp` timing consistency benchmark entry point
    - `transmitter/`: transmitter application
      - `main.cpp` transmitter application entry point
  - `lib/`: library source code
    - `contention_generator.cpp`: contention generator implementation
    - `contention_generator.hpp`: contention generator definition
    - `precise_sleep.cpp`: precise sleep implementation
    - `precise_sleep.hpp`: precise sleep definition
- `scripts/`: Experiments and Data analysis (runs transmitter/receiver for experiments and analyzes the traces)
  - `buffer_size_experiment.py` Changes the buffer size on both transmitter and receiver and runs combinations of experiments
  - `transmit_rate_experiments.py` Changes the frequency of data rate and runs experiments
  - `analysis.py` Calculates the accuracy of experiments
  - `print_bandwidth.py` Prints only bandwidths 
  - `emc_values.py` Calculates average/max EMC values 

### Setup

1. Build everything:

```bash
cmake -S . -B build
cmake --build build --parallel
```

2. Setup the analysis environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Copy and compile the GPU code 
Note (1st command): Paths may not match. In this case, just copy samples in cuda under ~/cuda_samples
Note (2nd command): Paths may not match. In this case, just the bandwidthTest.cu in our repo to cuda samples (replace it)

```bash
cp -r /usr/local/cuda/samples ~/cuda_samples
cp src/GPU_samples/bandwidthTest.cu ~/cuda_samples/1_Utilities/bandwidthTest/bandwidthTest.cu
cd ~/cuda_samples/1_Utilities/bandwidthTest
make
```

4. Run experiments for cpu (tranmistter) to gpu (receiver):

This experiment evaluates the effect of receiver size. (sensitivity analysis of receiver). More parameters can be modified to perform more experiments.

```bash
mkdir -p logs/cpu_to_gpu_receiver_buffer_size
python3 scripts/cpu_gpu.py --log_dir=logs/cpu_to_gpu_receiver_buffer_size
python3 scripts/analysis_microsecond.py --log_dir=logs/cpu_to_gpu_receiver_buffer_size --calculateAccuracy=History --threshold=0.05 --mergeFile=True
```



5. Run noise experiments


```bash
mkdir -p logs/cpu_to_gpu_noise_experiments
#This experiment have additional values for transmitter_values, receiver_values, time_switch_list (channel capacity )
python3 scripts/cpu_gpu.py --log_dir=logs/cpu_to_gpu_noise_experiments
#This experiment evaluates the accuracy without noise. Note that mergeFile argument creates a file with the traces to be easily evaluated. Merging once is enough. (check merge_files_with_transmitterTiming_and_receiverBW function and how/where it is called). "noise_percentage_values" values are dummy in this use since we don't use them while merging file for the first time.
python3 scripts/analysis_microsecond.py --log_dir=logs/cpu_to_gpu_noise_experiments --calculateAccuracy=History --threshold=0.05 --mergeFile=True
#This experiment generates the noise in the data and saves it to another file
python3 scripts/gaussian_noise_experiments.py
#This experiment evaluates the accuracy with noisy data. 
python3 scripts/analysis_microsecond.py --log_dir=logs/cpu_to_gpu_noise_experiments --calculateAccuracy=History --threshold=0.05 --mergeFile=False

```