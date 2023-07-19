# plot_live.py

import pandas as pd
import matplotlib.pyplot as plt


# Read the data from the file
data = pd.read_csv('data.csv')

# Convert the 'datetime' column to datetime objects
data['datetime'] = pd.to_datetime(data['datetime'])

# Set the 'datetime' column as the index
data.set_index('datetime', inplace=True)

# Plot the data
data['close'].plot()

# Save the plot as an image
plt.savefig('plot.png')

# Define the trading stats
stats = pd.read_csv('all_stats.csv')

# Convert the trading stats to an HTML table
stats_html = stats.to_html()

# Write the image and table to an HTML file
with open('report.html', 'w') as f:
    f.write('<img src="plot.png">\n')
    f.write(stats_html)

# Show the plot
plt.show()

