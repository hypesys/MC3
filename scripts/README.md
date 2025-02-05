# Scripts

## Documentation

### Usage

1. Run the either buffer size experiments or transmit rate experiments. (Both can be done separately.)

```bash
# Buffer size experiments. Buffer sizes are defined for both transmitter and receiver in script.
python3 scripts/buffer_size_experiments.py --log_dir=temp

# Transmit rate size experiments. Transmit rates are defined for transmitter in script. This script iterates over pre-defined transmit/receiver buffer size.
python3 scripts/transmit_rate_experiment.py --log_dir=temp


# Contention generation is completed X ms early to transmit bit 1. Early completion times are defined for transmitter in script. This script iterates over pre-defined transmit/receiver buffer size and transmit rate.
python3 scripts/transmit_rate_experiment.py --log_dir=temp

```

2. 

```bash
python3 scripts/analysis.py --log_dir=temp --iteration_count=32 --calculateAccuracy=History --threshold=0.1
```
