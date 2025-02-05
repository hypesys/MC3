#!/usr/bin/env python

from os.path import dirname, join, realpath
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

"""
Normalized thresholding hysterisis threshold
"""
hysteresis_threshold = 0.1

"""
Rolling average window size or 0 to only use a global average
"""
rolling_average_window_size = 0

"""
Number of samples between edges to consider them as separate edges
"""
edge_separation_samples = 7

"""
Tolerance for an edge to be considered a transition (relative to the extracted clock frequency)
"""
edge_transition_threshold = 0.5

"""
Graph view size (seconds) or 0 to show the entire graph
"""
graph_view_size = 0

"""
Graph view offset (seconds)
"""
graph_view_offset = 0

# Get the directory of the script
__dir__ = dirname(realpath(__file__))

# Read the CSV file into a DataFrame
df = pd.read_csv(join(__dir__, "bandwidth.csv"))
df["time"] = pd.to_datetime(df["time"], unit="ns")
df.set_index("time", inplace=True)

# Filter out nan values
df.dropna(inplace=True)

# Filter out warmup runs
df = df[df["type"] != "warmup"]
df.drop(columns=["type"], inplace=True)

# # Iterpolate the data to regular intervals
df = df.resample("25ms").mean().interpolate()

# Convert to numpy array
raw_bandwidth = df["bandwidth"].values
raw_bandwidth_x = (df.index - df.index[0]).total_seconds()

# Normalize the signal to have a mean of 0
normalized_bandwidth = (
    (raw_bandwidth - np.mean(raw_bandwidth)) / np.max(np.abs(raw_bandwidth))
    if rolling_average_window_size == 0
    else (
        raw_bandwidth
        - np.convolve(
            raw_bandwidth,
            np.ones(rolling_average_window_size) / rolling_average_window_size,
            mode="same",
        )
    )
    / np.max(np.abs(raw_bandwidth))
)

# Threshold the signal with hysteresis
thresholded_bandwidth = np.zeros(len(normalized_bandwidth))
last = False
for index, value in enumerate(normalized_bandwidth):
    if value > hysteresis_threshold:
        thresholded_bandwidth[index] = 1
        last = True
    elif value < -hysteresis_threshold:
        thresholded_bandwidth[index] = -1
        last = False
    else:
        thresholded_bandwidth[index] = 1 if last else -1

# Take the derivative
derived_bandwidth = np.diff(thresholded_bandwidth)

# Find the edges that are above the thresholds
edges = np.where(np.abs(derived_bandwidth))[0]

# Combine the edges that are too close together
edge_separation = 0
while edge_separation < len(edges) - 1:
    # Check if the edges are too close together
    if edges[edge_separation + 1] - edges[edge_separation] <= edge_separation_samples:
        # Combine the edges
        edges[edge_separation] = (
            edges[edge_separation] + edges[edge_separation + 1]
        ) // 2

        # Delete the next edge
        edges = np.delete(edges, edge_separation + 1)
    else:
        # Advance to the next edge
        edge_separation += 1

# Extract the clock frequency (the frequency with the largest sum of the first and second harmonics)
edge_frequencies = np.bincount(np.diff(edges))

if len(edge_frequencies) < 2:
    raise Exception("No edge frequencies detected!")

clock_frequency = 0
clock_frequency_harmonics_sum = edge_frequencies[0]

for edge_frequency_index in range(0, len(edge_frequencies) // 2):
    # Compute the current harmonics sum
    current_clock_frequency_harmonics_sum = (
        edge_frequencies[edge_frequency_index]
        + edge_frequencies[edge_frequency_index * 2]
    )

    # Update the clock frequency if the current harmonics sum is larger
    if current_clock_frequency_harmonics_sum > clock_frequency_harmonics_sum:
        clock_frequency = edge_frequency_index
        clock_frequency_harmonics_sum = current_clock_frequency_harmonics_sum

# Decode the data using differential manchester encoding (0 is transition, 1 is no transition)
bitstream = ""
bits = []
edge_index = 0
while edge_index < len(edges) - 1:
    # Compute the relative frequency mismatch of the number samples between the edges
    relative_frequency_mismatch_a = (
        abs(
            (edges[edge_index + 1] - edges[edge_index] - 1)
            - clock_frequency
        )
        / clock_frequency
    )
    relative_frequency_mismatch_b = (
        abs(
            (edges[edge_index + 2] - edges[edge_index + 1] - 1)
            - clock_frequency
        )
        / clock_frequency
        if edge_index < len(edges) - 2
        else None
    )

    # Check if the relative frequency mismatch is acceptable for a 0 bit (between 0 and edge_threshold)
    if (
        relative_frequency_mismatch_a <= edge_transition_threshold
        and relative_frequency_mismatch_b is not None
        and relative_frequency_mismatch_b <= edge_transition_threshold
        and edge_index < len(edges) - 2
    ):
        # Update the bit stream
        bitstream += "0"

        # Update the bits
        bits.append(
            {
                "x": (
                    raw_bandwidth_x[edges[edge_index]]
                    + raw_bandwidth_x[edges[edge_index + 2]]
                )
                / 2,
                "bit": 0,
            }
        )

        # Skip the next edge
        edge_index += 2

    # Check if the relative frequency mismatch is acceptable for a 1 (between 1 - edge_threshold and 1 + edge_threshold)
    elif (
        1 - edge_transition_threshold
        <= relative_frequency_mismatch_a
        <= 1 + edge_transition_threshold
    ):
        # Update the bit stream
        bitstream += "1"

        # Update the bits
        bits.append(
            {
                "x": (
                    raw_bandwidth_x[edges[edge_index]]
                    + raw_bandwidth_x[edges[edge_index + 1]]
                )
                / 2,
                "bit": 1,
            }
        )

        # Advance to the next edge
        edge_index += 1

    # Otherwise, the data is corrupted
    else:
        # Delete the edge
        edges = np.delete(edges, edge_index)

        # Advance to the next edge
        edge_index += 1

# Prepare the data for plotting
normalized_bandwidth_x = raw_bandwidth_x
normalized_bandwidth_y = normalized_bandwidth

thresholded_bandwidth_x = raw_bandwidth_x
thresholded_bandwidth_y = thresholded_bandwidth

derived_bandwidth_x = raw_bandwidth_x[1:]
derived_bandwidth_y = derived_bandwidth

edges_x = raw_bandwidth_x[edges]
edges_y = normalized_bandwidth_y[edges]

# Plot the data
plt.tight_layout()
fig, ax1 = plt.subplots(figsize=(10, 6))

ax1.plot(
    normalized_bandwidth_x,
    normalized_bandwidth_y,
    label="Normalized Bandwidth",
    color="tab:red",
)
ax1.plot(
    thresholded_bandwidth_x,
    thresholded_bandwidth_y,
    label="Thresholded Bandwidth",
    color="tab:green",
)
# ax1.plot(
#     derived_bandwidth_x,
#     derived_bandwidth_y,
#     label="Derived Bandwidth",
#     color="tab:blue",
# )
ax1.scatter(
    edges_x,
    edges_y,
    label="Edges",
    color="tab:purple",
    s=50,
)

# Add the bit labels
for bit in bits:
    # Skip if the bit is not in the view
    if bit["x"] < graph_view_offset or (graph_view_size != 0 and bit["x"] > graph_view_offset + graph_view_size):
        continue

    # Add the bit label
    ax1.text(
        bit["x"],
        0,
        str(bit["bit"]),
        horizontalalignment="center",
        verticalalignment="center",
        color="black",
        fontsize=12,
    )

# Set the graph limits
if graph_view_size != 0:
  ax1.set_xlim(graph_view_offset, graph_view_offset + graph_view_size)

# Set the graph labels
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Normalized Bandwidth")

# Set the graph legend
ax1.legend(loc="upper left")

# Save the plot as a PNG file
plt.savefig(join(__dir__, "graph.png"), dpi=300)

# Print the bit stream
print(f"Bits: {bitstream}")

# Convert the bit stream to its ASCII representation
ascii = ""
for edge_index in range(0, len(bitstream), 8):
    ascii += chr(int(bitstream[edge_index : edge_index + 8], 2))

# Print the ASCII representation
print(f"ASCII: {ascii}")
