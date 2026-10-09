import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("data/lap_traces.csv")      # Read .csv file
x_col = data.columns[0]                     # Select x-axis
y_col = data.columns[3]                     # Select y-axis

print("Columns in CSV", list(data.columns))

# Plotting data from x and y column
plt.plot(data[x_col], data[y_col], marker = 'o', linestyle = '-', color = 'green', linewidth = 0.2)
plt.plot(data[x_col], data[data.columns[7]], marker = 'o', linestyle = '-', color = 'red', linewidth = 0.2)
plt.title(f"{y_col} over {x_col}")
plt.xlabel(x_col)
plt.ylabel(y_col)
plt.grid(True)
plt.show()