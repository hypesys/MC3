# Receiver

## Documentation

### Usage

1. Run the receiver:

```bash
./build/receiver copy 0 32 4096 104857600 > ./src/experiments/receiver/bandwidth.csv
```

2. Run the transmitter (at the same time as the receiver, but only after the warmup is done):

```bash
# FYI: repeating capital U's will result in an alternating bit pattern
./build/transmitter copy 0 0 1073741824 "??? Hello, world! ???"
```

3. Analyze the results:

```bash
# Generates graph.png
./src/experiments/receiver/analyze.py
```
