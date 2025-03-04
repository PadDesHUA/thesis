### Fixes frequency in ARIMA and date restore

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
import os
from datetime import datetime
import pickle

# Directory paths
ath_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/ATH'
thes_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/THES'
data_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/DATA'

# Load data
athens_temperatures = pd.read_csv(os.path.join(ath_dir, 'weather_data_ath_pred.csv'))
thessaloniki_temperatures = pd.read_csv(os.path.join(thes_dir, 'weather_data_thess_pred.csv'))
internet_traffic = pd.read_csv(os.path.join(data_dir, 'output_data.csv'))

# Convert Date column to datetime format
today = datetime.today().strftime('%Y-%m-%d')
athens_temperatures["Date"] = pd.to_datetime(athens_temperatures["Date"], format="%Y/%b/%d")
thessaloniki_temperatures["Date"] = pd.to_datetime(thessaloniki_temperatures["Date"], format="%Y/%b/%d")
internet_traffic["Date"] = pd.to_datetime(internet_traffic["Date"], format="%Y/%m/%d")

# Set Date as index
internet_traffic.set_index("Date", inplace=True)
internet_traffic.index = internet_traffic.index.to_period('D')  # Explicitly set frequency

# Ensure stationarity for internet traffic
internet_traffic["DataInDiff"] = internet_traffic["DataIn(TB)"].diff().dropna()

# Train ARIMA model using last 4 days of available data
train_data = internet_traffic.iloc[-400:]["DataInDiff"].dropna()
model_traffic = ARIMA(train_data, order=(5,1,0))
model_traffic_fit = model_traffic.fit()

# Forecast from today to the next 4 days
last_date = internet_traffic.index[-1]  # Last available date in traffic data
forecast_dates = pd.date_range(start=last_date.to_timestamp(), periods=5, freq="D")

next_traffic_diff = model_traffic_fit.forecast(steps=5)
last_traffic = internet_traffic["DataIn(TB)"].iloc[-1]
next_traffic = last_traffic + np.cumsum(next_traffic_diff)
next_traffic[next_traffic < 0] = 0

# Merge weather forecast data with predicted traffic
forecast_df = pd.DataFrame({"Date": forecast_dates})
forecast_df = forecast_df.merge(athens_temperatures[["Date", "Avg"]], on="Date", how="left")
forecast_df = forecast_df.merge(thessaloniki_temperatures[["Date", "Avg"]], on="Date", how="left", suffixes=("_Athens", "_Thessaloniki"))
forecast_df["PredictedTraffic"] = next_traffic.values

# Save predictions to CSV
forecast_df.to_csv(f"{today}_prediction.csv", index=False)

# Plotting
fig, axs = plt.subplots(2, 1, figsize=(10, 12))
axs[0].plot(athens_temperatures["Date"], athens_temperatures["Avg"], label="Athens", color='blue')
axs[0].plot(thessaloniki_temperatures["Date"], thessaloniki_temperatures["Avg"], label="Thessaloniki", color='red')
axs[0].set_xlabel("Date")
axs[0].set_ylabel("Temperature (°C)")
axs[0].set_title("Temperature Data")
axs[0].legend()
axs[0].grid(True)

axs[1].plot(internet_traffic.index.to_timestamp(), internet_traffic["DataIn(TB)"], label="Internet Traffic", color='green')
axs[1].plot(forecast_dates, next_traffic, 'orange', linestyle='--', label='Predicted Traffic')
axs[1].set_xlabel("Date")
axs[1].set_ylabel("Internet Traffic (TB)")
axs[1].set_title("Internet Traffic Prediction")
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()
plt.savefig(f"{today}_traffic_prediction.png")  # Save the plot
plt.show()

# Remove the last 3 days from weather data before saving
athens_temperatures = athens_temperatures.iloc[:-3]
thessaloniki_temperatures = thessaloniki_temperatures.iloc[:-3]

# Restore original date format before saving
athens_temperatures["Date"] = athens_temperatures["Date"].dt.strftime("%Y/%b/%d")
thessaloniki_temperatures["Date"] = thessaloniki_temperatures["Date"].dt.strftime("%Y/%b/%d")
internet_traffic["Date"] = internet_traffic.index.to_timestamp().strftime("%Y/%m/%d")

if "Date" in internet_traffic.columns:
    internet_traffic.drop(columns=["Date"], inplace=True)

internet_traffic.reset_index(inplace=True)

# Save the updated files
athens_temperatures.to_csv(os.path.join(ath_dir, 'weather_data_ath_pred.csv'), index=False)
thessaloniki_temperatures.to_csv(os.path.join(thes_dir, 'weather_data_thess_pred.csv'), index=False)
internet_traffic.to_csv(os.path.join(data_dir, 'output_data.csv'), index=False)

# Save forecast and weather data for future comparison
with open(f"{today}_prediction_data.pkl", "wb") as f:
    pickle.dump({
        "forecast": forecast_df,
        "weather_athens": athens_temperatures,
        "weather_thessaloniki": thessaloniki_temperatures
    }, f)


# ### Saves output and repairs data file dates format. 
# ### also takes 3 months as training

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.arima.model import ARIMA
# import os
# from datetime import datetime
# import pickle

# # Directory paths
# ath_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/ATH'
# thes_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/THES'
# data_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/DATA'

# # Load data
# athens_temperatures = pd.read_csv(os.path.join(ath_dir, 'weather_data_ath_pred.csv'))
# thessaloniki_temperatures = pd.read_csv(os.path.join(thes_dir, 'weather_data_thess_pred.csv'))
# internet_traffic = pd.read_csv(os.path.join(data_dir, 'output_data.csv'))

# # Convert Date column to datetime format
# today = datetime.today().strftime('%Y-%m-%d')
# athens_temperatures["Date"] = pd.to_datetime(athens_temperatures["Date"], format="%Y/%b/%d")
# thessaloniki_temperatures["Date"] = pd.to_datetime(thessaloniki_temperatures["Date"], format="%Y/%b/%d")
# internet_traffic["Date"] = pd.to_datetime(internet_traffic["Date"], format="%Y/%m/%d")

# # Set Date as index
# internet_traffic.set_index("Date", inplace=True)

# # Ensure stationarity for internet traffic
# internet_traffic["DataInDiff"] = internet_traffic["DataIn(TB)"].diff().dropna()

# # Train ARIMA model using last 4 days of available data
# train_data = internet_traffic.iloc[-800:]["DataInDiff"].dropna()
# model_traffic = ARIMA(train_data, order=(5,1,0))
# model_traffic_fit = model_traffic.fit()

# # Forecast from today to the next 4 days
# last_date = internet_traffic.index[-1]  # Last available date in traffic data
# forecast_dates = pd.date_range(start=last_date, periods=5, freq="D")

# next_traffic_diff = model_traffic_fit.forecast(steps=5)
# last_traffic = internet_traffic["DataIn(TB)"].iloc[-1]
# next_traffic = last_traffic + np.cumsum(next_traffic_diff)
# next_traffic[next_traffic < 0] = 0

# # Merge weather forecast data with predicted traffic
# forecast_df = pd.DataFrame({"Date": forecast_dates})
# forecast_df = forecast_df.merge(athens_temperatures[["Date", "Avg"]], on="Date", how="left")
# forecast_df = forecast_df.merge(thessaloniki_temperatures[["Date", "Avg"]], on="Date", how="left", suffixes=("_Athens", "_Thessaloniki"))
# forecast_df["PredictedTraffic"] = next_traffic.values

# # Save predictions to CSV
# forecast_df.to_csv(f"{today}_prediction.csv", index=False)

# # Plotting
# fig, axs = plt.subplots(2, 1, figsize=(10, 12))
# axs[0].plot(athens_temperatures["Date"], athens_temperatures["Avg"], label="Athens", color='blue')
# axs[0].plot(thessaloniki_temperatures["Date"], thessaloniki_temperatures["Avg"], label="Thessaloniki", color='red')
# axs[0].set_xlabel("Date")
# axs[0].set_ylabel("Temperature (°C)")
# axs[0].set_title("Temperature Data")
# axs[0].legend()
# axs[0].grid(True)

# axs[1].plot(internet_traffic.index, internet_traffic["DataIn(TB)"], label="Internet Traffic", color='green')
# axs[1].plot(forecast_dates, next_traffic, 'orange', linestyle='--', label='Predicted Traffic')
# axs[1].set_xlabel("Date")
# axs[1].set_ylabel("Internet Traffic (TB)")
# axs[1].set_title("Internet Traffic Prediction")
# axs[1].legend()
# axs[1].grid(True)

# plt.tight_layout()
# plt.savefig(f"{today}_traffic_prediction.png")  # Save the plot
# plt.show()

# # Remove the last 3 days from weather data before saving
# athens_temperatures = athens_temperatures.iloc[:-3]
# thessaloniki_temperatures = thessaloniki_temperatures.iloc[:-3]

# # Restore original date format before saving
# athens_temperatures["Date"] = athens_temperatures["Date"].dt.strftime("%Y/%b/%d")
# thessaloniki_temperatures["Date"] = thessaloniki_temperatures["Date"].dt.strftime("%Y/%b/%d")
# internet_traffic["Date"] = internet_traffic.index.strftime("%Y/%m/%d")
# internet_traffic.reset_index(inplace=True)

# # Save the updated files
# athens_temperatures.to_csv(os.path.join(ath_dir, 'weather_data_ath_pred.csv'), index=False)
# thessaloniki_temperatures.to_csv(os.path.join(thes_dir, 'weather_data_thess_pred.csv'), index=False)
# internet_traffic.to_csv(os.path.join(data_dir, 'output_data.csv'), index=False)

# # Save forecast and weather data for future comparison
# with open(f"{today}_prediction_data.pkl", "wb") as f:
#     pickle.dump({
#         "forecast": forecast_df,
#         "weather_athens": athens_temperatures,
#         "weather_thessaloniki": thessaloniki_temperatures
#     }, f)



# ### Restore dateformat to input files
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.arima.model import ARIMA
# import os
# from datetime import datetime

# # Directory paths
# ath_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/ATH'
# thes_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/THES'
# data_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/DATA'

# # Load data
# athens_temperatures = pd.read_csv(os.path.join(ath_dir, 'weather_data_ath_pred.csv'))
# thessaloniki_temperatures = pd.read_csv(os.path.join(thes_dir, 'weather_data_thess_pred.csv'))
# internet_traffic = pd.read_csv(os.path.join(data_dir, 'output_data.csv'))

# # Convert Date column to datetime format
# today = datetime.today().strftime('%Y-%m-%d')
# athens_temperatures["Date"] = pd.to_datetime(athens_temperatures["Date"], format="%Y/%b/%d")
# thessaloniki_temperatures["Date"] = pd.to_datetime(thessaloniki_temperatures["Date"], format="%Y/%b/%d")
# internet_traffic["Date"] = pd.to_datetime(internet_traffic["Date"], format="%Y/%m/%d")

# # Set Date as index
# internet_traffic.set_index("Date", inplace=True)

# # Ensure stationarity for internet traffic
# internet_traffic["DataInDiff"] = internet_traffic["DataIn(TB)"].diff().dropna()

# # Train ARIMA model using last 4 days of available data
# train_data = internet_traffic.iloc[-400:]["DataInDiff"].dropna()
# model_traffic = ARIMA(train_data, order=(5,1,0))
# model_traffic_fit = model_traffic.fit()

# # Forecast from today to the next 4 days
# #forecast_dates = pd.date_range(start=today, periods=5, freq="D")
# last_date = internet_traffic.index[-1]  # Last available date in traffic data
# forecast_dates = pd.date_range(start=last_date, periods=5, freq="D")


# next_traffic_diff = model_traffic_fit.forecast(steps=5)
# last_traffic = internet_traffic["DataIn(TB)"].iloc[-1]
# next_traffic = last_traffic + np.cumsum(next_traffic_diff)
# next_traffic[next_traffic < 0] = 0

# # Merge weather forecast data with predicted traffic for consistency
# forecast_df = pd.DataFrame({"Date": forecast_dates})
# forecast_df = forecast_df.merge(athens_temperatures[["Date", "Avg"]], on="Date", how="left")
# forecast_df = forecast_df.merge(thessaloniki_temperatures[["Date", "Avg"]], on="Date", how="left", suffixes=("_Athens", "_Thessaloniki"))
# forecast_df["PredictedTraffic"] = next_traffic.values

# # Save predictions to CSV
# forecast_df.to_csv(f"{today}_prediction.csv", index=False)

# # Plotting
# fig, axs = plt.subplots(2, 1, figsize=(10, 12))

# # Plot temperature data
# axs[0].plot(athens_temperatures["Date"], athens_temperatures["Avg"], label="Athens", color='blue')
# axs[0].plot(thessaloniki_temperatures["Date"], thessaloniki_temperatures["Avg"], label="Thessaloniki", color='red')
# axs[0].set_xlabel("Date")
# axs[0].set_ylabel("Temperature (°C)")
# axs[0].set_title("Temperature Data")
# axs[0].legend()
# axs[0].grid(True)

# # Plot internet traffic
# axs[1].plot(internet_traffic.index, internet_traffic["DataIn(TB)"], label="Internet Traffic", color='green')
# axs[1].plot(forecast_dates, next_traffic, 'orange', linestyle='--', label='Predicted Traffic')
# axs[1].set_xlabel("Date")
# axs[1].set_ylabel("Internet Traffic (TB)")
# axs[1].set_title("Internet Traffic Prediction")
# axs[1].legend()
# axs[1].grid(True)

# # Align x-axis range based on available data
# overall_start = min(internet_traffic.index.min(), athens_temperatures["Date"].min(), thessaloniki_temperatures["Date"].min())
# overall_end = max(forecast_dates.max(), athens_temperatures["Date"].max(), thessaloniki_temperatures["Date"].max())
# for ax in axs:
#     ax.set_xlim(overall_start, overall_end)

# plt.tight_layout()
# plt.show()

# # Restore original date format before saving
# athens_temperatures["Date"] = athens_temperatures["Date"].dt.strftime("%Y/%b/%d")
# thessaloniki_temperatures["Date"] = thessaloniki_temperatures["Date"].dt.strftime("%Y/%b/%d")
# internet_traffic["Date"] = internet_traffic.index.strftime("%Y/%m/%d")
# #internet_traffic.reset_index(inplace=True)
# if "Date" in internet_traffic.columns:
#     internet_traffic.drop(columns=["Date"], inplace=True)  # Remove duplicate "Date" column

# internet_traffic.reset_index(inplace=True)  # Now safe to reset index



# # Save the updated files
# athens_temperatures.to_csv(os.path.join(ath_dir, 'weather_data_ath_pred.csv'), index=False)
# thessaloniki_temperatures.to_csv(os.path.join(thes_dir, 'weather_data_thess_pred.csv'), index=False)
# internet_traffic.to_csv(os.path.join(data_dir, 'output_data.csv'), index=False)


### This version can delete also before exiting the code, the last entries from weather data csv
### Changes dates in source files

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.arima.model import ARIMA
# import os
# from datetime import datetime

# # Directory paths
# ath_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/ATH'
# thes_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/THES'
# data_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/DATA'

# # Load data
# athens_temperatures = pd.read_csv(os.path.join(ath_dir, 'weather_data_ath_pred.csv'))
# thessaloniki_temperatures = pd.read_csv(os.path.join(thes_dir, 'weather_data_thess_pred.csv'))
# internet_traffic = pd.read_csv(os.path.join(data_dir, 'output_data.csv'))

# # Convert Date column to datetime format
# today = datetime.today().strftime('%Y-%m-%d')
# athens_temperatures["Date"] = pd.to_datetime(athens_temperatures["Date"], format="%Y/%b/%d")
# thessaloniki_temperatures["Date"] = pd.to_datetime(thessaloniki_temperatures["Date"], format="%Y/%b/%d")
# internet_traffic["Date"] = pd.to_datetime(internet_traffic["Date"], format="%Y/%m/%d")

# # Set Date as index
# internet_traffic.set_index("Date", inplace=True)

# # Ensure stationarity for internet traffic
# internet_traffic["DataInDiff"] = internet_traffic["DataIn(TB)"].diff().dropna()

# # Train ARIMA model using last 4 days of available data
# train_data = internet_traffic.iloc[-4:]["DataInDiff"].dropna()
# model_traffic = ARIMA(train_data, order=(5,1,0))
# model_traffic_fit = model_traffic.fit()

# # Forecast from today to the next 4 days
# forecast_dates = pd.date_range(start=today, periods=5, freq="D")
# next_traffic_diff = model_traffic_fit.forecast(steps=5)
# last_traffic = internet_traffic["DataIn(TB)"].iloc[-1]
# next_traffic = last_traffic + np.cumsum(next_traffic_diff)
# next_traffic[next_traffic < 0] = 0

# # Merge weather forecast data with predicted traffic for consistency
# forecast_df = pd.DataFrame({"Date": forecast_dates})
# forecast_df = forecast_df.merge(athens_temperatures[["Date", "Avg"]], on="Date", how="left")
# forecast_df = forecast_df.merge(thessaloniki_temperatures[["Date", "Avg"]], on="Date", how="left", suffixes=("_Athens", "_Thessaloniki"))
# forecast_df["PredictedTraffic"] = next_traffic.values

# # Save predictions to CSV
# forecast_df.to_csv(f"{today}_prediction.csv", index=False)

# # Plotting
# fig, axs = plt.subplots(2, 1, figsize=(10, 12))

# # Plot temperature data
# axs[0].plot(athens_temperatures["Date"], athens_temperatures["Avg"], label="Athens", color='blue')
# axs[0].plot(thessaloniki_temperatures["Date"], thessaloniki_temperatures["Avg"], label="Thessaloniki", color='red')
# axs[0].set_xlabel("Date")
# axs[0].set_ylabel("Temperature (°C)")
# axs[0].set_title("Temperature Data")
# axs[0].legend()
# axs[0].grid(True)

# # Plot internet traffic
# axs[1].plot(internet_traffic.index, internet_traffic["DataIn(TB)"], label="Internet Traffic", color='green')
# axs[1].plot(forecast_dates, next_traffic, 'orange', linestyle='--', label='Predicted Traffic')
# axs[1].set_xlabel("Date")
# axs[1].set_ylabel("Internet Traffic (TB)")
# axs[1].set_title("Internet Traffic Prediction")
# axs[1].legend()
# axs[1].grid(True)

# # Align x-axis range based on available data
# overall_start = min(internet_traffic.index.min(), athens_temperatures["Date"].min(), thessaloniki_temperatures["Date"].min())
# overall_end = max(forecast_dates.max(), athens_temperatures["Date"].max(), thessaloniki_temperatures["Date"].max())
# for ax in axs:
#     ax.set_xlim(overall_start, overall_end)

# plt.tight_layout()
# plt.show()

# # Delete future weather data after today
# for weather_file in [os.path.join(ath_dir, 'weather_data_ath_pred.csv'), os.path.join(thes_dir, 'weather_data_thess_pred.csv')]:
#     weather_df = pd.read_csv(weather_file)
#     weather_df["Date"] = pd.to_datetime(weather_df["Date"], format="%Y/%b/%d")
#     weather_df = weather_df[weather_df["Date"] <= today]
#     weather_df.to_csv(weather_file, index=False)




# ### Previous version is fine for the MSc. Now this version add the csv output with arima results and weater forecast

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.arima.model import ARIMA
# import os
# from datetime import datetime

# # Directory paths
# ath_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/ATH'
# thes_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/THES'
# data_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/DATA'

# # Load data
# athens_temperatures = pd.read_csv(os.path.join(ath_dir, 'weather_data_ath_pred.csv'))
# thessaloniki_temperatures = pd.read_csv(os.path.join(thes_dir, 'weather_data_thess_pred.csv'))
# internet_traffic = pd.read_csv(os.path.join(data_dir, 'output_data.csv'))

# # Convert Date column to datetime format
# athens_temperatures["Date"] = pd.to_datetime(athens_temperatures["Date"], format="%Y/%b/%d")
# thessaloniki_temperatures["Date"] = pd.to_datetime(thessaloniki_temperatures["Date"], format="%Y/%b/%d")
# internet_traffic["Date"] = pd.to_datetime(internet_traffic["Date"], format="%Y/%m/%d")

# # Set Date as index
# internet_traffic.set_index("Date", inplace=True)

# # Ensure stationarity for internet traffic
# internet_traffic["DataInDiff"] = internet_traffic["DataIn(TB)"].diff().dropna()

# # Train ARIMA model using last 4 days of available data
# train_data = internet_traffic.loc["2025-02-20":"2025-02-23", "DataInDiff"].dropna()
# model_traffic = ARIMA(train_data, order=(5,1,0))
# model_traffic_fit = model_traffic.fit()

# # Forecast from 24th to 28th February 2025
# forecast_dates = pd.date_range(start="2025-02-24", periods=5, freq="D")
# next_traffic_diff = model_traffic_fit.forecast(steps=5)
# last_traffic = internet_traffic.loc["2025-02-23", "DataIn(TB)"]
# next_traffic = last_traffic + np.cumsum(next_traffic_diff)
# next_traffic[next_traffic < 0] = 0

# # Merge weather forecast data with predicted traffic for consistency
# forecast_df = pd.DataFrame({"Date": forecast_dates})
# forecast_df = forecast_df.merge(athens_temperatures[["Date", "Avg"]], on="Date", how="left")
# forecast_df = forecast_df.merge(thessaloniki_temperatures[["Date", "Avg"]], on="Date", how="left", suffixes=("_Athens", "_Thessaloniki"))
# forecast_df["PredictedTraffic"] = next_traffic.values

# # Save predictions to CSV
# current_date = datetime.today().strftime('%Y%m%d')
# forecast_df.to_csv(f"{current_date}_prediction.csv", index=False)

# # Plotting
# fig, axs = plt.subplots(2, 1, figsize=(10, 12))

# # Plot temperature data
# axs[0].plot(athens_temperatures["Date"], athens_temperatures["Avg"], label="Athens", color='blue')
# axs[0].plot(thessaloniki_temperatures["Date"], thessaloniki_temperatures["Avg"], label="Thessaloniki", color='red')
# axs[0].set_xlabel("Date")
# axs[0].set_ylabel("Temperature (°C)")
# axs[0].set_title("Temperature Data")
# axs[0].legend()
# axs[0].grid(True)

# # Plot internet traffic
# axs[1].plot(internet_traffic.index, internet_traffic["DataIn(TB)"], label="Internet Traffic", color='green')
# axs[1].plot(forecast_dates, next_traffic, 'orange', linestyle='--', label='Predicted Traffic')
# axs[1].set_xlabel("Date")
# axs[1].set_ylabel("Internet Traffic (TB)")
# axs[1].set_title("Internet Traffic Prediction")
# axs[1].legend()
# axs[1].grid(True)

# # Align x-axis range based on available data
# overall_start = min(internet_traffic.index.min(), athens_temperatures["Date"].min(), thessaloniki_temperatures["Date"].min())
# overall_end = max(forecast_dates.max(), athens_temperatures["Date"].max(), thessaloniki_temperatures["Date"].max())
# for ax in axs:
#     ax.set_xlim(overall_start, overall_end)

# plt.tight_layout()
# plt.show()




# ### WORKING!!!

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.arima.model import ARIMA
# import os

# # Directory paths
# ath_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/ATH'
# thes_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/THES'
# data_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/DATA'

# # Load data
# athens_temperatures = pd.read_csv(os.path.join(ath_dir, 'weather_data_ath_pred.csv'))
# thessaloniki_temperatures = pd.read_csv(os.path.join(thes_dir, 'weather_data_thess_pred.csv'))
# internet_traffic = pd.read_csv(os.path.join(data_dir, 'output_data.csv'))

# # Convert Date column to datetime format
# athens_temperatures["Date"] = pd.to_datetime(athens_temperatures["Date"], format="%Y/%b/%d")
# thessaloniki_temperatures["Date"] = pd.to_datetime(thessaloniki_temperatures["Date"], format="%Y/%b/%d")
# internet_traffic["Date"] = pd.to_datetime(internet_traffic["Date"], format="%Y/%m/%d")

# # Set Date as index
# internet_traffic.set_index("Date", inplace=True)

# # Ensure stationarity for internet traffic
# internet_traffic["DataInDiff"] = internet_traffic["DataIn(TB)"].diff().dropna()

# # Train ARIMA model using last 4 days of available data
# train_data = internet_traffic.loc["2025-02-20":"2025-02-23", "DataInDiff"].dropna()
# model_traffic = ARIMA(train_data, order=(5,1,0))
# model_traffic_fit = model_traffic.fit()

# # Forecast from 24th to 28th February 2025
# forecast_dates = pd.date_range(start="2025-02-24", periods=5, freq="D")
# next_traffic_diff = model_traffic_fit.forecast(steps=5)
# last_traffic = internet_traffic.loc["2025-02-23", "DataIn(TB)"]
# next_traffic = last_traffic + np.cumsum(next_traffic_diff)
# next_traffic[next_traffic < 0] = 0

# # Plotting
# fig, axs = plt.subplots(2, 1, figsize=(10, 12))

# # Plot temperature data
# axs[0].plot(athens_temperatures["Date"], athens_temperatures["Avg"], label="Athens", color='blue')
# axs[0].plot(thessaloniki_temperatures["Date"], thessaloniki_temperatures["Avg"], label="Thessaloniki", color='red')
# axs[0].set_xlabel("Date")
# axs[0].set_ylabel("Temperature (°C)")
# axs[0].set_title("Temperature Data")
# axs[0].legend()
# axs[0].grid(True)

# # Plot internet traffic
# axs[1].plot(internet_traffic.index, internet_traffic["DataIn(TB)"], label="Internet Traffic", color='green')
# axs[1].plot(forecast_dates, next_traffic, 'orange', linestyle='--', label='Predicted Traffic')
# axs[1].set_xlabel("Date")
# axs[1].set_ylabel("Internet Traffic (TB)")
# axs[1].set_title("Internet Traffic Prediction")
# axs[1].legend()
# axs[1].grid(True)

# # Align x-axis range based on available data
# overall_start = min(internet_traffic.index.min(), athens_temperatures["Date"].min(), thessaloniki_temperatures["Date"].min())
# overall_end = max(forecast_dates.max(), athens_temperatures["Date"].max(), thessaloniki_temperatures["Date"].max())
# for ax in axs:
#     ax.set_xlim(overall_start, overall_end)

# plt.tight_layout()
# plt.show()

# ### WORKING -> minor changes to fine tune it are needed

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.arima.model import ARIMA
# from sklearn.linear_model import LinearRegression
# import os

# # Directory paths
# ath_dir = '/home/itp22109/Documents/HUA/HUA MSc/\u03a7\u03b5\u03b9\u03bc\u03b5\u03c1\u03b9\u03bd\u03cc 2023/\u0394\u03b9\u03c0\u03bb\u03c9\u03bc\u03b1\u03c4\u03b9\u03ba\u03ae/GIT_repo/ATH'
# thes_dir = '/home/itp22109/Documents/HUA/HUA MSc/\u03a7\u03b5\u03b9\u03bc\u03b5\u03c1\u03b9\u03bd\u03cc 2023/\u0394\u03b9\u03c0\u03bb\u03c9\u03bc\u03b1\u03c4\u03b9\u03ba\u03ae/GIT_repo/THES'
# data_dir = '/home/itp22109/Documents/HUA/HUA MSc/\u03a7\u03b5\u03b9\u03bc\u03b5\u03c1\u03b9\u03bd\u03cc 2023/\u0394\u03b9\u03c0\u03bb\u03c9\u03bc\u03b1\u03c4\u03b9\u03ba\u03ae/GIT_repo/DATA'

# # Load data
# athens_temperatures = pd.read_csv(os.path.join(ath_dir, 'weather_data_ath_pred.csv'))
# thessaloniki_temperatures = pd.read_csv(os.path.join(thes_dir, 'weather_data_thess_pred.csv'))
# internet_traffic = pd.read_csv(os.path.join(data_dir, 'output_data.csv'))

# # Convert Date column to datetime format
# athens_temperatures["Date"] = pd.to_datetime(athens_temperatures["Date"], format="%Y/%b/%d")
# thessaloniki_temperatures["Date"] = pd.to_datetime(thessaloniki_temperatures["Date"], format="%Y/%b/%d")
# internet_traffic["Date"] = pd.to_datetime(internet_traffic["Date"], format="%Y/%m/%d")

# # Set Date as index
# internet_traffic.set_index("Date", inplace=True)

# # Ensure stationarity for internet traffic
# internet_traffic["DataInDiff"] = internet_traffic["DataIn(TB)"].diff().dropna()

# # Train ARIMA model using last 4 days of available data
# train_data = internet_traffic.loc["2025-02-20":"2025-02-23", "DataInDiff"].dropna()
# model_traffic = ARIMA(train_data, order=(5,1,0))
# model_traffic_fit = model_traffic.fit()

# # Forecast from 24th to 28th February 2025
# forecast_dates = pd.date_range(start="2025-02-24", periods=5, freq="D")
# next_traffic_diff = model_traffic_fit.forecast(steps=5)
# last_traffic = internet_traffic.loc["2025-02-23", "DataIn(TB)"]
# next_traffic = last_traffic + np.cumsum(next_traffic_diff)
# next_traffic[next_traffic < 0] = 0

# # Plotting
# fig, axs = plt.subplots(2, 1, figsize=(10, 12))

# # Plot temperature data
# axs[0].plot(athens_temperatures["Date"], athens_temperatures["Avg"], label="Athens", color='blue')
# axs[0].plot(thessaloniki_temperatures["Date"], thessaloniki_temperatures["Avg"], label="Thessaloniki", color='red')
# axs[0].set_xlabel("Date")
# axs[0].set_ylabel("Temperature (°C)")
# axs[0].set_title("Temperature Data")
# axs[0].legend()
# axs[0].grid(True)

# # Plot internet traffic
# axs[1].plot(internet_traffic.index, internet_traffic["DataIn(TB)"], label="Internet Traffic", color='green')
# axs[1].plot(forecast_dates, next_traffic, 'orange', linestyle='--', label='Predicted Traffic')
# axs[1].set_xlabel("Date")
# axs[1].set_ylabel("Internet Traffic (TB)")
# axs[1].set_title("Internet Traffic Prediction")
# axs[1].legend()
# axs[1].grid(True)

# # Align x-axis range
# for ax in axs:
#     ax.set_xlim(pd.to_datetime("2025-02-20"), pd.to_datetime("2025-02-28"))

# plt.tight_layout()
# plt.show()



# ###  WORKING but thte ploting needs fine tuning also the ARIMA only in output data

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.arima.model import ARIMA
# from sklearn.linear_model import LinearRegression
# import os

# # Directory paths
# ath_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/ATH'
# thes_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/THES'
# data_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/DATA'

# # Load data from CSV files
# athens_temperatures = pd.read_csv(os.path.join(ath_dir, 'weather_data_ath_pred.csv'), parse_dates=["Date"])
# thessaloniki_temperatures = pd.read_csv(os.path.join(thes_dir, 'weather_data_thess_pred.csv'), parse_dates=["Date"])
# internet_traffic = pd.read_csv(os.path.join(data_dir, 'output_data.csv'), parse_dates=["Date"])

# # Convert Date column to datetime format
# internet_traffic["Date"] = pd.to_datetime(internet_traffic["Date"], format="%Y/%m/%d")
# athens_temperatures["Date"] = pd.to_datetime(athens_temperatures["Date"], format="%Y/%b/%d")
# thessaloniki_temperatures["Date"] = pd.to_datetime(thessaloniki_temperatures["Date"], format="%Y/%b/%d")

# # Set "Date" column as index
# internet_traffic.set_index("Date", inplace=True)

# # ARIMA Model for Internet Traffic
# model_traffic = ARIMA(internet_traffic["DataIn(TB)"], order=(5,1,0))
# model_traffic_fit = model_traffic.fit()

# # Forecast internet traffic from 24th to 28th Feb 2025
# forecast_dates = pd.date_range(start="2025-02-24", periods=5, freq="D")
# traffic_forecast = model_traffic_fit.forecast(steps=5)
# traffic_forecast[traffic_forecast < 0] = 0  # Ensure no negative values
# last_traffic = internet_traffic["DataIn(TB)"].iloc[-1]
# predicted_traffic = last_traffic + np.cumsum(traffic_forecast)

# # Linear Regression Model for Weather Data
# recent_athens_temps = athens_temperatures[athens_temperatures["Date"] >= "2025-02-21"]
# recent_thess_temps = thessaloniki_temperatures[thessaloniki_temperatures["Date"] >= "2025-02-21"]

# X_athens = recent_athens_temps["Date"].dt.dayofyear.values.reshape(-1, 1)
# y_athens = recent_athens_temps["Avg"].values
# model_athens = LinearRegression()
# model_athens.fit(X_athens, y_athens)

# X_thess = recent_thess_temps["Date"].dt.dayofyear.values.reshape(-1, 1)
# y_thess = recent_thess_temps["Avg"].values
# model_thess = LinearRegression()
# model_thess.fit(X_thess, y_thess)

# # Predict temperatures for 25th to 28th Feb 2025
# next_days_temp = forecast_dates.dayofyear.values.reshape(-1, 1)
# next_temperatures_athens = model_athens.predict(next_days_temp)
# next_temperatures_thess = model_thess.predict(next_days_temp)

# # Plotting
# fig, axs = plt.subplots(2, 1, figsize=(10, 12))

# # Plot temperature predictions
# axs[0].plot(athens_temperatures["Date"], athens_temperatures["Avg"], label="Avg Temperature Athens", color='blue')
# axs[0].plot(thessaloniki_temperatures["Date"], thessaloniki_temperatures["Avg"], label="Avg Temperature Thessaloniki", color='red')
# axs[0].plot(forecast_dates, next_temperatures_athens, 'g--', label='Predicted Athens')
# axs[0].plot(forecast_dates, next_temperatures_thess, 'm--', label='Predicted Thessaloniki')
# axs[0].set_xlabel("Date")
# axs[0].set_ylabel("Temperature (°C)")
# axs[0].set_title("Temperature Data with Predictions")
# axs[0].legend()
# axs[0].grid(True)

# # Plot internet traffic predictions
# axs[1].plot(internet_traffic.index, internet_traffic["DataIn(TB)"], label="Internet Traffic", color='green')
# axs[1].plot(forecast_dates, predicted_traffic, 'orange', linestyle='--', label='Predicted Traffic')
# axs[1].set_xlabel("Date")
# axs[1].set_ylabel("Internet Traffic (TB)")
# axs[1].set_title("Internet Traffic Data with ARIMA Predictions")
# axs[1].legend()
# axs[1].grid(True)

# # Align x-axis across both plots
# for ax in axs:
#     ax.set_xlim(athens_temperatures["Date"].min(), forecast_dates[-1])

# plt.tight_layout()
# plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.5)
# plt.show()
# plt.savefig('output_plot.png')



# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.arima.model import ARIMA
# from sklearn.linear_model import LinearRegression
# import os

# # Directory paths
# ath_dir = '/home/itp22109/Documents/HUA/HUA MSc/\u03a7\u03b5\u03b9\u03bc\u03b5\u03c1\u03b9\u03bd\u03cc 2023/\u0394\u03b9\u03c0\u03bb\u03c9\u03bc\u03b1\u03c4\u03b9\u03ba\u03ae/GIT_repo/ATH'
# thes_dir = '/home/itp22109/Documents/HUA/HUA MSc/\u03a7\u03b5\u03b9\u03bc\u03b5\u03c1\u03b9\u03bd\u03cc 2023/\u0394\u03b9\u03c0\u03bb\u03c9\u03bc\u03b1\u03c4\u03b9\u03ba\u03ae/GIT_repo/THES'
# data_dir = '/home/itp22109/Documents/HUA/HUA MSc/\u03a7\u03b5\u03b9\u03bc\u03b5\u03c1\u03b9\u03bd\u03cc 2023/\u0394\u03b9\u03c0\u03bb\u03c9\u03bc\u03b1\u03c4\u03b9\u03ba\u03ae/GIT_repo/DATA'

# # Load data
# athens_temperatures = pd.read_csv(os.path.join(ath_dir, 'weather_data_ath_pred.csv'))
# thessaloniki_temperatures = pd.read_csv(os.path.join(thes_dir, 'weather_data_thess_pred.csv'))
# internet_traffic = pd.read_csv(os.path.join(data_dir, 'output_data.csv'))

# # Convert Date column to datetime format
# athens_temperatures['Date'] = pd.to_datetime(athens_temperatures['Date'], format='%Y/%b/%d')
# thessaloniki_temperatures['Date'] = pd.to_datetime(thessaloniki_temperatures['Date'], format='%Y/%b/%d')
# internet_traffic['Date'] = pd.to_datetime(internet_traffic['Date'], format='%Y/%m/%d')

# # Set Date as index with frequency
# for df in [internet_traffic, athens_temperatures, thessaloniki_temperatures]:
#     df.set_index('Date', inplace=True)
#     df.sort_index(inplace=True)

# # Ensure stationarity function
# def ensure_stationarity(series):
#     result = adfuller(series.dropna())
#     if result[1] > 0.05:
#         return series.diff().dropna()
#     return series

# # Ensure stationarity for internet traffic
# internet_traffic['DataInDiff'] = ensure_stationarity(internet_traffic.iloc[:, 1])

# # Use last 4 days of weather data for prediction
# today = pd.Timestamp('2025-02-24')
# forecast_dates = pd.date_range(start=today + pd.Timedelta(days=1), periods=4, freq='D')

# # Fit ARIMA model for internet traffic
# data_diff = internet_traffic['DataInDiff'].dropna()
# model_traffic = ARIMA(data_diff, order=(5,1,0))
# model_traffic_fit = model_traffic.fit()

# # Predict next 4 days
# next_traffic_diff = model_traffic_fit.forecast(steps=4)
# last_traffic = internet_traffic.iloc[-1, 1]
# next_traffic = last_traffic + np.cumsum(next_traffic_diff)
# next_traffic[next_traffic < 0] = 0

# # Combine actual and predicted data
# date_range_full = pd.date_range(start=internet_traffic.index.min(), end=forecast_dates[-1])
# internet_traffic_full = internet_traffic.reindex(date_range_full).interpolate()
# predicted_traffic = pd.Series(next_traffic, index=forecast_dates)

# # Plotting
# fig, ax = plt.subplots(figsize=(12, 6))

# ax.plot(internet_traffic_full.index, internet_traffic_full.iloc[:, 1], label='Internet Traffic', color='green')
# ax.plot(predicted_traffic.index, predicted_traffic, 'orange', linestyle='--', label='Predicted Traffic')
# ax.set_xlabel("Date")
# ax.set_ylabel("Internet Traffic (TB)")
# ax.set_title("Internet Traffic Data with Predictions")
# ax.legend()
# ax.grid(True)

# # Twin axis for temperature
# twin_ax = ax.twinx()
# twin_ax.plot(athens_temperatures.index, athens_temperatures.iloc[:, 1], label="Athens Temperature", color='blue')
# twin_ax.plot(thessaloniki_temperatures.index, thessaloniki_temperatures.iloc[:, 1], label="Thessaloniki Temperature", color='red')
# twin_ax.set_ylabel("Temperature (°C)")

# # Set the same x-axis range
# ax.set_xlim(internet_traffic.index.min(), forecast_dates[-1])

# plt.legend()
# plt.show()


# ### WORKING but only with internet usage plot and also cover the first date ploting

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.arima.model import ARIMA
# from sklearn.linear_model import LinearRegression
# import os

# # Directory paths
# ath_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/ATH'
# thes_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/THES'
# data_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/DATA'

# # Load data
# athens_temperatures = pd.read_csv(os.path.join(ath_dir, 'weather_data_ath_pred.csv'))
# thessaloniki_temperatures = pd.read_csv(os.path.join(thes_dir, 'weather_data_thess_pred.csv'))
# internet_traffic = pd.read_csv(os.path.join(data_dir, 'output_data.csv'))

# # Convert Date column to datetime format
# athens_temperatures['Date'] = pd.to_datetime(athens_temperatures['Date'], format='%Y/%b/%d')
# thessaloniki_temperatures['Date'] = pd.to_datetime(thessaloniki_temperatures['Date'], format='%Y/%b/%d')
# internet_traffic['Date'] = pd.to_datetime(internet_traffic['Date'], format='%Y/%m/%d')

# # Set Date as index with frequency
# def set_index_with_freq(df):
#     df.set_index('Date', inplace=True)
#     df = df.asfreq('D')  # Explicitly setting daily frequency
#     return df

# internet_traffic = set_index_with_freq(internet_traffic)
# athens_temperatures = set_index_with_freq(athens_temperatures)
# thessaloniki_temperatures = set_index_with_freq(thessaloniki_temperatures)

# # Function to check and ensure stationarity
# def ensure_stationarity(series):
#     result = adfuller(series.dropna())
#     if result[1] > 0.05:  # Not stationary, require differencing
#         series_diff = series.diff().dropna()
#         result = adfuller(series_diff.dropna())
#         if result[1] > 0.05:
#             return series_diff.diff().dropna()  # Second differencing if still not stationary
#         return series_diff
#     return series

# # Ensure stationarity for internet traffic
# internet_traffic['DataInDiff'] = ensure_stationarity(internet_traffic.iloc[:, 1])

# # Use last 4 days of weather data for prediction
# today = pd.Timestamp('2025-02-24')
# forecast_dates = pd.date_range(start=today + pd.Timedelta(days=1), periods=4, freq='D')

# # Fit ARIMA model for internet traffic
# data_diff = internet_traffic['DataInDiff'].dropna()
# model_traffic = ARIMA(data_diff, order=(5,1,0))
# model_traffic_fit = model_traffic.fit()

# # Predict next 4 days
# next_traffic_diff = model_traffic_fit.forecast(steps=4)
# last_traffic = internet_traffic.iloc[-1, 1]
# next_traffic = last_traffic + np.cumsum(next_traffic_diff)
# next_traffic[next_traffic < 0] = 0  # Ensure no negative values

# # Plotting
# fig, ax = plt.subplots(figsize=(10, 6))
# ax.plot(internet_traffic.index, internet_traffic.iloc[:, 1], label='Internet Traffic', color='green')
# ax.plot(forecast_dates, next_traffic, 'orange', linestyle='--', label='Predicted Traffic')
# ax.legend()
# ax.grid(True)
# ax.set_xlim(internet_traffic.index.min(), forecast_dates[-1])
# plt.tight_layout()
# plt.show()


# ###WORKING -< Fine tuning the prediction of internet traffic for the last 4 days based on the weather forecast

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.arima.model import ARIMA
# from sklearn.linear_model import LinearRegression
# import os

# # Directory paths
# ath_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/ATH'
# thes_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/THES'
# data_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/DATA'

# # Load data
# athens_temperatures = pd.read_csv(os.path.join(ath_dir, 'weather_data_ath_pred.csv'))
# thessaloniki_temperatures = pd.read_csv(os.path.join(thes_dir, 'weather_data_thess_pred.csv'))
# internet_traffic = pd.read_csv(os.path.join(data_dir, 'output_data.csv'))

# # Convert Date column to datetime format
# athens_temperatures['Date'] = pd.to_datetime(athens_temperatures['Date'])
# thessaloniki_temperatures['Date'] = pd.to_datetime(thessaloniki_temperatures['Date'])
# internet_traffic['Date'] = pd.to_datetime(internet_traffic['Date'])

# # Set Date as index with frequency
# def set_index_with_freq(df):
#     df.set_index('Date', inplace=True)
#     df = df.asfreq('D')  # Explicitly setting daily frequency
#     return df

# internet_traffic = set_index_with_freq(internet_traffic)
# athens_temperatures = set_index_with_freq(athens_temperatures)
# thessaloniki_temperatures = set_index_with_freq(thessaloniki_temperatures)

# # Function to check and ensure stationarity
# def ensure_stationarity(series):
#     result = adfuller(series.dropna())
#     if result[1] > 0.05:  # Not stationary, require differencing
#         series_diff = series.diff().dropna()
#         result = adfuller(series_diff.dropna())
#         if result[1] > 0.05:
#             return series_diff.diff().dropna()  # Second differencing if still not stationary
#         return series_diff
#     return series

# # Ensure stationarity for internet traffic
# internet_traffic['DataInDiff'] = ensure_stationarity(internet_traffic['DataIn(TB)'])

# # Ensure stationarity for temperature data
# athens_temperatures['AvgDiff'] = ensure_stationarity(athens_temperatures['Avg'])
# thessaloniki_temperatures['AvgDiff'] = ensure_stationarity(thessaloniki_temperatures['Avg'])

# # Fit ARIMA model for internet traffic
# data_diff = internet_traffic['DataInDiff'].dropna()
# model_traffic = ARIMA(data_diff, order=(5,1,0))
# model_traffic_fit = model_traffic.fit()

# # Predict next 3 days
# next_traffic_diff = model_traffic_fit.forecast(steps=3)
# last_traffic = internet_traffic['DataIn(TB)'].iloc[-1]
# next_traffic = last_traffic + np.cumsum(next_traffic_diff)
# next_traffic[next_traffic < 0] = 0  # Ensure no negative values

# # Fit Linear Regression models for temperature prediction
# athens_temperatures.dropna(subset=['AvgDiff'], inplace=True)
# thessaloniki_temperatures.dropna(subset=['AvgDiff'], inplace=True)

# X_athens = athens_temperatures.index.dayofyear.values.reshape(-1, 1)
# y_athens = athens_temperatures['AvgDiff'].values
# model_athens = LinearRegression().fit(X_athens, y_athens)

# X_thessaloniki = thessaloniki_temperatures.index.dayofyear.values.reshape(-1, 1)
# y_thessaloniki = thessaloniki_temperatures['AvgDiff'].values
# model_thessaloniki = LinearRegression().fit(X_thessaloniki, y_thessaloniki)

# # Predict temperatures for the next 3 days
# next_dates_temp = pd.date_range(start=athens_temperatures.index.max() + pd.Timedelta(days=1), periods=3, freq='D')
# next_days_athens = next_dates_temp.dayofyear.values.reshape(-1, 1)
# next_temperatures_athens_diff = model_athens.predict(next_days_athens)
# last_temp_athens = athens_temperatures['Avg'].iloc[-1]
# next_temperatures_athens = last_temp_athens + np.cumsum(next_temperatures_athens_diff)

# next_days_thessaloniki = next_dates_temp.dayofyear.values.reshape(-1, 1)
# next_temperatures_thessaloniki_diff = model_thessaloniki.predict(next_days_thessaloniki)
# last_temp_thessaloniki = thessaloniki_temperatures['Avg'].iloc[-1]
# next_temperatures_thessaloniki = last_temp_thessaloniki + np.cumsum(next_temperatures_thessaloniki_diff)

# # Plotting
# fig, axs = plt.subplots(2, 1, figsize=(10, 12), sharex=True)

# # Plot Temperature Data
# axs[0].plot(athens_temperatures.index, athens_temperatures['Avg'], label='Athens Temp', color='blue')
# axs[0].plot(thessaloniki_temperatures.index, thessaloniki_temperatures['Avg'], label='Thessaloniki Temp', color='red')
# axs[0].plot(next_dates_temp, next_temperatures_athens, 'g--', label='Predicted Athens')
# axs[0].plot(next_dates_temp, next_temperatures_thessaloniki, 'm--', label='Predicted Thessaloniki')
# axs[0].legend()
# axs[0].grid(True)

# # Plot Internet Traffic Data
# axs[1].plot(internet_traffic.index, internet_traffic['DataIn(TB)'], label='Internet Traffic', color='green')
# axs[1].plot(next_dates_temp, next_traffic, 'orange', linestyle='--', label='Predicted Traffic')
# axs[1].legend()
# axs[1].grid(True)

# # Set the same x-axis range for both plots
# axs[0].set_xlim(athens_temperatures.index.min(), next_dates_temp[-1])
# axs[1].set_xlim(athens_temperatures.index.min(), next_dates_temp[-1])

# plt.tight_layout()
# plt.show()



# ###Working but needs to align the plots on interesting dates of the data date range

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.arima.model import ARIMA
# from sklearn.linear_model import LinearRegression
# import os

# # Directory paths
# ath_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/ATH'
# thes_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/THES'
# data_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/DATA'

# # Load data
# athens_temperatures = pd.read_csv(os.path.join(ath_dir, 'weather_data_ath_pred.csv'))
# thessaloniki_temperatures = pd.read_csv(os.path.join(thes_dir, 'weather_data_thess_pred.csv'))
# internet_traffic = pd.read_csv(os.path.join(data_dir, 'output_data.csv'))

# # Convert Date column to datetime format
# athens_temperatures['Date'] = pd.to_datetime(athens_temperatures['Date'])
# thessaloniki_temperatures['Date'] = pd.to_datetime(thessaloniki_temperatures['Date'])
# internet_traffic['Date'] = pd.to_datetime(internet_traffic['Date'])

# # Set Date as index with frequency
# def set_index_with_freq(df):
#     df.set_index('Date', inplace=True)
#     df = df.asfreq('D')  # Explicitly setting daily frequency
#     return df

# internet_traffic = set_index_with_freq(internet_traffic)
# athens_temperatures = set_index_with_freq(athens_temperatures)
# thessaloniki_temperatures = set_index_with_freq(thessaloniki_temperatures)

# # Function to check and ensure stationarity
# def ensure_stationarity(series):
#     result = adfuller(series.dropna())
#     if result[1] > 0.05:  # Not stationary, require differencing
#         series_diff = series.diff().dropna()
#         result = adfuller(series_diff.dropna())
#         if result[1] > 0.05:
#             return series_diff.diff().dropna()  # Second differencing if still not stationary
#         return series_diff
#     return series

# # Ensure stationarity for internet traffic
# internet_traffic['DataInDiff'] = ensure_stationarity(internet_traffic['DataIn(TB)'])

# # Ensure stationarity for temperature data
# athens_temperatures['AvgDiff'] = ensure_stationarity(athens_temperatures['Avg'])
# thessaloniki_temperatures['AvgDiff'] = ensure_stationarity(thessaloniki_temperatures['Avg'])

# # Fit ARIMA model for internet traffic
# data_diff = internet_traffic['DataInDiff'].dropna()
# model_traffic = ARIMA(data_diff, order=(5,1,0))
# model_traffic_fit = model_traffic.fit()

# # Predict next 3 days
# next_traffic_diff = model_traffic_fit.forecast(steps=3)
# last_traffic = internet_traffic['DataIn(TB)'].iloc[-1]
# next_traffic = last_traffic + np.cumsum(next_traffic_diff)
# next_traffic[next_traffic < 0] = 0  # Ensure no negative values

# # Fit Linear Regression models for temperature prediction
# athens_temperatures.dropna(subset=['AvgDiff'], inplace=True)
# thessaloniki_temperatures.dropna(subset=['AvgDiff'], inplace=True)

# X_athens = athens_temperatures.index.dayofyear.values.reshape(-1, 1)
# y_athens = athens_temperatures['AvgDiff'].values
# model_athens = LinearRegression().fit(X_athens, y_athens)

# X_thessaloniki = thessaloniki_temperatures.index.dayofyear.values.reshape(-1, 1)
# y_thessaloniki = thessaloniki_temperatures['AvgDiff'].values
# model_thessaloniki = LinearRegression().fit(X_thessaloniki, y_thessaloniki)

# # Predict temperatures for the next 3 days
# next_dates_temp = pd.date_range(start=athens_temperatures.index.max() + pd.Timedelta(days=1), periods=3, freq='D')
# next_days_athens = next_dates_temp.dayofyear.values.reshape(-1, 1)
# next_temperatures_athens_diff = model_athens.predict(next_days_athens)
# last_temp_athens = athens_temperatures['Avg'].iloc[-1]
# next_temperatures_athens = last_temp_athens + np.cumsum(next_temperatures_athens_diff)

# next_days_thessaloniki = next_dates_temp.dayofyear.values.reshape(-1, 1)
# next_temperatures_thessaloniki_diff = model_thessaloniki.predict(next_days_thessaloniki)
# last_temp_thessaloniki = thessaloniki_temperatures['Avg'].iloc[-1]
# next_temperatures_thessaloniki = last_temp_thessaloniki + np.cumsum(next_temperatures_thessaloniki_diff)

# # Plotting
# fig, axs = plt.subplots(2, 1, figsize=(10, 12))

# # Plot Temperature Data
# axs[0].plot(athens_temperatures.index, athens_temperatures['Avg'], label='Athens Temp', color='blue')
# axs[0].plot(thessaloniki_temperatures.index, thessaloniki_temperatures['Avg'], label='Thessaloniki Temp', color='red')
# axs[0].plot(next_dates_temp, next_temperatures_athens, 'g--', label='Predicted Athens')
# axs[0].plot(next_dates_temp, next_temperatures_thessaloniki, 'm--', label='Predicted Thessaloniki')
# axs[0].legend()
# axs[0].grid(True)

# # Plot Internet Traffic Data
# axs[1].plot(internet_traffic.index, internet_traffic['DataIn(TB)'], label='Internet Traffic', color='green')
# axs[1].plot(next_dates_temp, next_traffic, 'orange', linestyle='--', label='Predicted Traffic')
# axs[1].legend()
# axs[1].grid(True)

# plt.tight_layout()
# plt.show()



#### Working partially with error in differential

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.arima.model import ARIMA
# from sklearn.linear_model import LinearRegression
# from sklearn.preprocessing import StandardScaler
# import os

# # Directory paths
# ath_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/ATH'
# thes_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/THES'
# data_dir = '/home/itp22109/Documents/HUA/HUA MSc/Χειμερινό 2023/Διπλωματική/GIT_repo/DATA'

# # Load data from CSV files in the respective directories
# athens_temperatures = pd.read_csv(os.path.join(ath_dir, 'weather_data_ath_pred.csv'))
# thessaloniki_temperatures = pd.read_csv(os.path.join(thes_dir, 'weather_data_thess_pred.csv'))
# internet_traffic = pd.read_csv(os.path.join(data_dir, 'output_data.csv'))

# # Convert Date column to datetime format
# athens_temperatures["Date"] = pd.to_datetime(athens_temperatures["Date"])
# thessaloniki_temperatures["Date"] = pd.to_datetime(thessaloniki_temperatures["Date"])
# internet_traffic["Date"] = pd.to_datetime(internet_traffic["Date"])

# # Set the "Date" column as index for proper ARIMA model handling
# internet_traffic.set_index("Date", inplace=True)

# # Function to check and ensure stationarity
# def check_stationarity(series):
#     result = adfuller(series.dropna())
#     print('ADF Statistic:', result[0])
#     print('p-value:', result[1])
#     if result[1] > 0.05:
#         print("Series is not stationary. Differencing is required.")
#         return False
#     else:
#         print("Series is stationary.")
#         return True

# # Ensure stationarity for internet traffic
# if not check_stationarity(internet_traffic["DataIn(TB)"]):
#     internet_traffic["DataInDiff"] = internet_traffic["DataIn(TB)"].diff().dropna()
# else:
#     internet_traffic["DataInDiff"] = internet_traffic["DataIn(TB)"]

# # Ensure stationarity for temperature data
# if not check_stationarity(athens_temperatures["Avg"]):
#     athens_temperatures["AvgDiff"] = athens_temperatures["Avg"].diff().dropna()
# else:
#     athens_temperatures["AvgDiff"] = athens_temperatures["Avg"]

# if not check_stationarity(thessaloniki_temperatures["Avg"]):
#     thessaloniki_temperatures["AvgDiff"] = thessaloniki_temperatures["Avg"].diff().dropna()
# else:
#     thessaloniki_temperatures["AvgDiff"] = thessaloniki_temperatures["Avg"]

# # Fit ARIMA model for internet traffic
# model_traffic = ARIMA(internet_traffic["DataInDiff"].dropna(), order=(5,1,0))
# model_traffic_fit = model_traffic.fit()

# # Predict internet traffic for the next 3 days
# next_traffic_diff = model_traffic_fit.forecast(steps=3)
# last_traffic = internet_traffic["DataIn(TB)"].iloc[-1]
# next_traffic = last_traffic + np.cumsum(next_traffic_diff)
# next_traffic[next_traffic < 0] = 0  # Ensure no negative values

# # Fit linear regression model for Athens temperatures
# athens_temperatures = athens_temperatures.dropna(subset=["AvgDiff"])
# X_athens = athens_temperatures["Date"].dt.dayofyear.values.reshape(-1, 1)
# y_athens = athens_temperatures["AvgDiff"].values
# model_athens = LinearRegression()
# model_athens.fit(X_athens, y_athens)

# # Fit linear regression model for Thessaloniki temperatures
# thessaloniki_temperatures = thessaloniki_temperatures.dropna(subset=["AvgDiff"])
# X_thessaloniki = thessaloniki_temperatures["Date"].dt.dayofyear.values.reshape(-1, 1)
# y_thessaloniki = thessaloniki_temperatures["AvgDiff"].values
# model_thessaloniki = LinearRegression()
# model_thessaloniki.fit(X_thessaloniki, y_thessaloniki)

# # Predict temperatures for the next 3 days
# last_date_temp = athens_temperatures["Date"].max()
# next_dates_temp = pd.date_range(start=last_date_temp + pd.Timedelta(days=1), periods=3, freq="D")

# next_days_athens = next_dates_temp.dayofyear.values.reshape(-1, 1)
# next_temperatures_athens_diff = model_athens.predict(next_days_athens)
# last_temp_athens = athens_temperatures["Avg"].iloc[-1]
# next_temperatures_athens = last_temp_athens + np.cumsum(next_temperatures_athens_diff)

# next_days_thessaloniki = next_dates_temp.dayofyear.values.reshape(-1, 1)
# next_temperatures_thessaloniki_diff = model_thessaloniki.predict(next_days_thessaloniki)
# last_temp_thessaloniki = thessaloniki_temperatures["Avg"].iloc[-1]
# next_temperatures_thessaloniki = last_temp_thessaloniki + np.cumsum(next_temperatures_thessaloniki_diff)

# # Plotting
# fig, axs = plt.subplots(2, 1, figsize=(10, 12))

# # Plotting temperature data for Athens and Thessaloniki
# axs[0].plot(athens_temperatures["Date"], athens_temperatures["Avg"], label="Avg Temperature Athens", color='blue')
# axs[0].plot(thessaloniki_temperatures["Date"], thessaloniki_temperatures["Avg"], label="Avg Temperature Thessaloniki", color='red')
# axs[0].plot(next_dates_temp, next_temperatures_athens, 'g--', label='Predicted Athens')
# axs[0].plot(next_dates_temp, next_temperatures_thessaloniki, 'm--', label='Predicted Thessaloniki')
# axs[0].set_xlabel("Date")
# axs[0].set_ylabel("Temperature (°C)")
# axs[0].set_title("Temperature Data for Athens and Thessaloniki with Predictions")
# axs[0].legend()
# axs[0].grid(True)

# # Plotting internet traffic data
# axs[1].plot(internet_traffic.index, internet_traffic["DataIn(TB)"], label="Internet Traffic", color='green')
# axs[1].plot(next_dates_temp, next_traffic, 'orange', linestyle='--', label='Predicted Traffic')
# axs[1].set_xlabel("Date")
# axs[1].set_ylabel("Internet Traffic (TB)")
# axs[1].set_title("Internet Traffic Data with ARIMA Predictions")
# axs[1].legend()
# axs[1].grid(True)

# # Set the same x-axis range for both plots
# for ax in axs:
#     ax.set_xlim(athens_temperatures["Date"].min(), next_dates_temp[-1])

# plt.tight_layout()
# plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.5)

# # Display the plot
# plt.show(block=False)

# #Alternatively, save the plot to a file if needed
# plt.savefig('output_plot.png')



# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.arima.model import ARIMA
# from sklearn.linear_model import LinearRegression
# from sklearn.preprocessing import StandardScaler

# # Load data from CSV files
# athens_temperatures = pd.read_csv('weather_data_ath.csv')
# thessaloniki_temperatures = pd.read_csv('weather_thess.csv')
# internet_traffic = pd.read_csv('internet_usage_converted.csv')

# # Convert Date column to datetime format
# athens_temperatures["Date"] = pd.to_datetime(athens_temperatures["Date"])
# thessaloniki_temperatures["Date"] = pd.to_datetime(thessaloniki_temperatures["Date"])
# internet_traffic["Date"] = pd.to_datetime(internet_traffic["Date"])

# # Set the "Date" column as index for proper ARIMA model handling
# internet_traffic.set_index("Date", inplace=True)

# # Function to check and ensure stationarity
# def check_stationarity(series):
#     result = adfuller(series.dropna())
#     print('ADF Statistic:', result[0])
#     print('p-value:', result[1])
#     if result[1] > 0.05:
#         print("Series is not stationary. Differencing is required.")
#         return False
#     else:
#         print("Series is stationary.")
#         return True

# # Ensure stationarity for internet traffic
# if not check_stationarity(internet_traffic["DataIn(TB)"]):
#     internet_traffic["DataInDiff"] = internet_traffic["DataIn(TB)"].diff().dropna()
# else:
#     internet_traffic["DataInDiff"] = internet_traffic["DataIn(TB)"]

# # Ensure stationarity for temperature data
# if not check_stationarity(athens_temperatures["Avg"]):
#     athens_temperatures["AvgDiff"] = athens_temperatures["Avg"].diff().dropna()
# else:
#     athens_temperatures["AvgDiff"] = athens_temperatures["Avg"]

# if not check_stationarity(thessaloniki_temperatures["Avg"]):
#     thessaloniki_temperatures["AvgDiff"] = thessaloniki_temperatures["Avg"].diff().dropna()
# else:
#     thessaloniki_temperatures["AvgDiff"] = thessaloniki_temperatures["Avg"]

# # Fit ARIMA model for internet traffic
# model_traffic = ARIMA(internet_traffic["DataInDiff"].dropna(), order=(5,1,0))
# model_traffic_fit = model_traffic.fit()

# # Predict internet traffic for the next 3 days
# next_traffic_diff = model_traffic_fit.forecast(steps=3)
# last_traffic = internet_traffic["DataIn(TB)"].iloc[-1]
# next_traffic = last_traffic + np.cumsum(next_traffic_diff)
# next_traffic[next_traffic < 0] = 0  # Ensure no negative values

# # Fit linear regression model for Athens temperatures
# athens_temperatures = athens_temperatures.dropna(subset=["AvgDiff"])
# X_athens = athens_temperatures["Date"].dt.dayofyear.values.reshape(-1, 1)
# y_athens = athens_temperatures["AvgDiff"].values
# model_athens = LinearRegression()
# model_athens.fit(X_athens, y_athens)

# # Fit linear regression model for Thessaloniki temperatures
# thessaloniki_temperatures = thessaloniki_temperatures.dropna(subset=["AvgDiff"])
# X_thessaloniki = thessaloniki_temperatures["Date"].dt.dayofyear.values.reshape(-1, 1)
# y_thessaloniki = thessaloniki_temperatures["AvgDiff"].values
# model_thessaloniki = LinearRegression()
# model_thessaloniki.fit(X_thessaloniki, y_thessaloniki)

# # Predict temperatures for the next 3 days
# last_date_temp = athens_temperatures["Date"].max()
# next_dates_temp = pd.date_range(start=last_date_temp + pd.Timedelta(days=1), periods=3, freq="D")

# next_days_athens = next_dates_temp.dayofyear.values.reshape(-1, 1)
# next_temperatures_athens_diff = model_athens.predict(next_days_athens)
# last_temp_athens = athens_temperatures["Avg"].iloc[-1]
# next_temperatures_athens = last_temp_athens + np.cumsum(next_temperatures_athens_diff)

# next_days_thessaloniki = next_dates_temp.dayofyear.values.reshape(-1, 1)
# next_temperatures_thessaloniki_diff = model_thessaloniki.predict(next_days_thessaloniki)
# last_temp_thessaloniki = thessaloniki_temperatures["Avg"].iloc[-1]
# next_temperatures_thessaloniki = last_temp_thessaloniki + np.cumsum(next_temperatures_thessaloniki_diff)

# # Plotting
# fig, axs = plt.subplots(2, 1, figsize=(10, 12))

# # Plotting temperature data for Athens and Thessaloniki
# axs[0].plot(athens_temperatures["Date"], athens_temperatures["Avg"], label="Avg Temperature Athens", color='blue')
# axs[0].plot(thessaloniki_temperatures["Date"], thessaloniki_temperatures["Avg"], label="Avg Temperature Thessaloniki", color='red')
# axs[0].plot(next_dates_temp, next_temperatures_athens, 'g--', label='Predicted Athens')
# axs[0].plot(next_dates_temp, next_temperatures_thessaloniki, 'm--', label='Predicted Thessaloniki')
# axs[0].set_xlabel("Date")
# axs[0].set_ylabel("Temperature (°C)")
# axs[0].set_title("Temperature Data for Athens and Thessaloniki with Predictions")
# axs[0].legend()
# axs[0].grid(True)

# # Plotting internet traffic data
# axs[1].plot(internet_traffic.index, internet_traffic["DataIn(TB)"], label="Internet Traffic", color='green')
# axs[1].plot(next_dates_temp, next_traffic, 'orange', linestyle='--', label='Predicted Traffic')
# axs[1].set_xlabel("Date")
# axs[1].set_ylabel("Internet Traffic (GB)")
# axs[1].set_title("Internet Traffic Data with ARIMA Predictions")
# axs[1].legend()
# axs[1].grid(True)

# # Set the same x-axis range for both plots
# for ax in axs:
#     ax.set_xlim(athens_temperatures["Date"].min(), next_dates_temp[-1])

# plt.tight_layout()
# plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.5)

# # Display the plot
# plt.show(block=False)

# # Alternatively, save the plot to a file if needed
# # plt.savefig('output_plot.png')

