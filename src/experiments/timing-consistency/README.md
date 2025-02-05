# Timing Consistency Benchmark

## Documentation

### Usage

1. Run the benchmark:

```bash
./build/timing-consistency run-for 10000 1000000 copy 0 1073741824 > ./src/experiments/timing-consistency/error.csv
```

2. Analyze the results:

```bash
# Generates graph.png
./src/experiments/timing-consistency/analyze.py
```

### Flamegraph

1. Build with debug symbols:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug && cmake --build build --parallel
```

2. Run the benchmark:

```bash
sudo perf record --call-graph dwarf --output ./src/experiments/timing-consistency/results.perf ./build/timing-consistency run-for 32 1000000 copy 0 10485760
```

3. Generate the flamegraph:

```bash
sudo chown $USER:$USER ./src/experiments/timing-consistency/results.perf
sudo chmod 644 ./src/experiments/timing-consistency/results.perf
perf script --input ./src/experiments/timing-consistency/results.perf | ./utils/flamegraph/stackcollapse-perf.pl | ./utils/flamegraph/flamegraph.pl > ./src/experiments/timing-consistency/results.svg
