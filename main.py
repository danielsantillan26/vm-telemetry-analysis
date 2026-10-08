import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("data/lap_traces.csv")      # Read .csv file
x_col = data.columns[0]                     # Select x-axis
y_col = data.columns[1]                     # Select y-axis

print("Columns in CSV", list(data.columns))

# Plotting data from x and y column
plt.plot(data[x_col], data[y_col], marker = 'o', linestyle = '-', color = 'green')
plt.plot(data[x_col], data[data.columns[2]], marker = 'o', linestyle = '-', color = 'red')
plt.title(f"{y_col} over {x_col}")
plt.xlabel(x_col)
plt.ylabel(y_col)
plt.grid(True)
plt.show()