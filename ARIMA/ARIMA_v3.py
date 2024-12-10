import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# Load data from CSV files
athens_temperatures = pd.read_csv('weather_data_ath.csv')
thessaloniki_temperatures = pd.read_csv('weather_thess.csv')
internet_traffic = pd.read_csv('internet_usage_converted.csv')

# Convert Date column to datetime format
athens_temperatures["Date"] = pd.to_datetime(athens_temperatures["Date"])
thessaloniki_temperatures["Date"] = pd.to_datetime(thessaloniki_temperatures["Date"])
internet_traffic["Date"] = pd.to_datetime(internet_traffic["Date"])

# Set the "Date" column as index for proper ARIMA model handling
internet_traffic.set_index("Date", inplace=True)

# Function to check and ensure stationarity
def check_stationarity(series):
    result = adfuller(series.dropna())
    print('ADF Statistic:', result[0])
    print('p-value:', result[1])
    if result[1] > 0.05:
        print("Series is not stationary. Differencing is required.")
        return False
    else:
        print("Series is stationary.")
        return True

# Ensure stationarity for internet traffic
if not check_stationarity(internet_traffic["DataIn(GB)"]):
    internet_traffic["DataInDiff"] = internet_traffic["DataIn(GB)"].diff().dropna()
else:
    internet_traffic["DataInDiff"] = internet_traffic["DataIn(GB)"]

# Ensure stationarity for temperature data
if not check_stationarity(athens_temperatures["Avg"]):
    athens_temperatures["AvgDiff"] = athens_temperatures["Avg"].diff().dropna()
else:
    athens_temperatures["AvgDiff"] = athens_temperatures["Avg"]

if not check_stationarity(thessaloniki_temperatures["Avg"]):
    thessaloniki_temperatures["AvgDiff"] = thessaloniki_temperatures["Avg"].diff().dropna()
else:
    thessaloniki_temperatures["AvgDiff"] = thessaloniki_temperatures["Avg"]

# Fit ARIMA model for internet traffic
model_traffic = ARIMA(internet_traffic["DataInDiff"].dropna(), order=(5,1,0))
model_traffic_fit = model_traffic.fit()

# Predict internet traffic for the next 3 days
next_traffic_diff = model_traffic_fit.forecast(steps=3)
last_traffic = internet_traffic["DataIn(GB)"].iloc[-1]
next_traffic = last_traffic + np.cumsum(next_traffic_diff)
next_traffic[next_traffic < 0] = 0  # Ensure no negative values

# Fit linear regression model for Athens temperatures
athens_temperatures = athens_temperatures.dropna(subset=["AvgDiff"])
X_athens = athens_temperatures["Date"].dt.dayofyear.values.reshape(-1, 1)
y_athens = athens_temperatures["AvgDiff"].values
model_athens = LinearRegression()
model_athens.fit(X_athens, y_athens)

# Fit linear regression model for Thessaloniki temperatures
thessaloniki_temperatures = thessaloniki_temperatures.dropna(subset=["AvgDiff"])
X_thessaloniki = thessaloniki_temperatures["Date"].dt.dayofyear.values.reshape(-1, 1)
y_thessaloniki = thessaloniki_temperatures["AvgDiff"].values
model_thessaloniki = LinearRegression()
model_thessaloniki.fit(X_thessaloniki, y_thessaloniki)

# Predict temperatures for the next 3 days
last_date_temp = athens_temperatures["Date"].max()
next_dates_temp = pd.date_range(start=last_date_temp + pd.Timedelta(days=1), periods=3, freq="D")

next_days_athens = next_dates_temp.dayofyear.values.reshape(-1, 1)
next_temperatures_athens_diff = model_athens.predict(next_days_athens)
last_temp_athens = athens_temperatures["Avg"].iloc[-1]
next_temperatures_athens = last_temp_athens + np.cumsum(next_temperatures_athens_diff)

next_days_thessaloniki = next_dates_temp.dayofyear.values.reshape(-1, 1)
next_temperatures_thessaloniki_diff = model_thessaloniki.predict(next_days_thessaloniki)
last_temp_thessaloniki = thessaloniki_temperatures["Avg"].iloc[-1]
next_temperatures_thessaloniki = last_temp_thessaloniki + np.cumsum(next_temperatures_thessaloniki_diff)

# Plotting
fig, axs = plt.subplots(2, 1, figsize=(10, 12))

# Plotting temperature data for Athens and Thessaloniki
axs[0].plot(athens_temperatures["Date"], athens_temperatures["Avg"], label="Avg Temperature Athens", color='blue')
axs[0].plot(thessaloniki_temperatures["Date"], thessaloniki_temperatures["Avg"], label="Avg Temperature Thessaloniki", color='red')
axs[0].plot(next_dates_temp, next_temperatures_athens, 'g--', label='Predicted Athens')
axs[0].plot(next_dates_temp, next_temperatures_thessaloniki, 'm--', label='Predicted Thessaloniki')
axs[0].set_xlabel("Date")
axs[0].set_ylabel("Temperature (°C)")
axs[0].set_title("Temperature Data for Athens and Thessaloniki with Predictions")
axs[0].legend()
axs[0].grid(True)

# Plotting internet traffic data
axs[1].plot(internet_traffic.index, internet_traffic["DataIn(GB)"], label="Internet Traffic", color='green')
axs[1].plot(next_dates_temp, next_traffic, 'orange', linestyle='--', label='Predicted Traffic')
axs[1].set_xlabel("Date")
axs[1].set_ylabel("Internet Traffic (GB)")
axs[1].set_title("Internet Traffic Data with ARIMA Predictions")
axs[1].legend()
axs[1].grid(True)

# Set the same x-axis range for both plots
for ax in axs:
    ax.set_xlim(athens_temperatures["Date"].min(), next_dates_temp[-1])

plt.tight_layout()
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.5)

# Display the plot
plt.show(block=False)

# Alternatively, save the plot to a file if needed
# plt.savefig('output_plot.png')

