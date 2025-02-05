#!/usr/bin/env python

from os.path import dirname, join, realpath
import matplotlib.pyplot as plt
import pandas as pd

# Get the directory of the script
__dir__ = dirname(realpath(__file__))

# Read the CSV file into a DataFrame
df = pd.read_csv(join(__dir__, "error.csv"))

# Plot the data
plt.tight_layout()
fig, ax1 = plt.subplots(figsize=(10, 6))

ax1.plot(
    df["iteration"],
    df["error"],
)

# Set the graph labels
ax1.set_xlabel("Iteration")
ax1.set_ylabel("Error (ns)")

# Save the plot as a PNG file
plt.savefig(join(__dir__, "graph.png"), dpi=300)
