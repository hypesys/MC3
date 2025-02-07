# Covert Channel

## Documentation

### Structure

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

<!-- 2. Setup the analysis environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
``` -->

2. Copy and compile the GPU code. We basically modified the bandwidthTest.cu sample from CUDA samples and used it as GPU receiver.
Note (1st command): Paths may not match. In this case, just copy samples in cuda under ~/cuda_samples
Note (2nd command): Paths may not match. In this case, just the bandwidthTest.cu in our repo to cuda samples (replace it)

```bash
cp -r /usr/local/cuda/samples ~/cuda_samples
cp src/GPU_samples/bandwidthTest.cu ~/cuda_samples/1_Utilities/bandwidthTest/bandwidthTest.cu
cd ~/cuda_samples/1_Utilities/bandwidthTest
make
```

3. Run experiments for cpu (tranmistter) to gpu (receiver):

This experiment evaluates receiver buffer size. (sensitivity analysis of receiver). More parameters can be modified to perform more experiments, some of which are left under comments as suggestions.

```bash
mkdir -p logs/cpu_to_gpu_receiver_buffer_size
python3 scripts/cpu_gpu.py --log_dir=logs/cpu_to_gpu_receiver_buffer_size
python3 scripts/analysis_microsecond.py --log_dir=logs/cpu_to_gpu_receiver_buffer_size --calculateAccuracy=History --threshold=0.05 --mergeFile=True
```

