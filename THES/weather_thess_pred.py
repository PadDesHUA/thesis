
#Try to repair parsing 

import csv
import os
import re
import time
from datetime import date, datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# Path to your ChromeDriver executable
chrome_driver_path = '/usr/local/bin/chromedriver'

# Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Today's date
today = date.today()

# Check if CSV exists and load existing dates
csv_file_path = 'weather_data_ath_pred.csv'
existing_dates = set()
last_date = None

if os.path.isfile(csv_file_path) and os.path.getsize(csv_file_path) > 0:
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # Skip the header row
        for line in reader:
            if line:
                date_str = line[0]  # Date in first column
                existing_dates.add(date_str)
                last_date = date_str  # Track the last date found in CSV

# Determine if historical data collection is needed
go_to_forecast = (last_date == today.strftime('%Y/%b/%d'))

# Open the CSV file in append mode
with open(csv_file_path, 'a', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)

    # Add CSV header if it's a new file
    if os.path.getsize(csv_file_path) == 0:
        csvwriter.writerow(['Date', 'Max', 'Avg', 'Min'])  # Header

    # Forecast Section for the next 3 days
    for day in range(1, 4):
        forecast_date = today + timedelta(days=day)
        forecast_date_str = forecast_date.strftime('%Y/%b/%d')  # For CSV format
        display_date_str = forecast_date.strftime('%a %m/%d')  # For website display

        # Open forecast page
        forecast_url = "https://www.wunderground.com/forecast/gr/athens"
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(forecast_url)

        # max_retries = 3
        # retry_count = 0
        
        try:
            # Handle cookie consent popup if present
            try:
                cookie_popup_iframe = WebDriverWait(driver, 10).until(
                    EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe[title="SP Consent Message"]'))
                )
                accept_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Accept all"]'))
                )
                accept_button.click()



                driver.switch_to.default_content()

                button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[id="wuSettings"]'))
                    )
                button.click()

                    # Wait for forecast data
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_element_located((By.XPATH, "//div[contains(@class, 'obs-date')]"))
                )

                # Retrieve forecast data
                forecast_data_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_element_located((
                        By.XPATH, "/html/body/app-root/app-tenday/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[2]/section/div[3]/div[1]/div/div[1]/div/lib-forecast-chart/div/div/div/lib-forecast-chart-header-daily/div/div"
                    ))
                )


                link_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="wuSettings-quick"]/div/a[2]'))
                    )
                link_element.click()
                break

            except Exception as e:
                print("No cookie consent popup:", e)


            # Wait for forecast data
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'obs-date')]"))
            )

            # Retrieve forecast data
            forecast_data_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((
                    By.XPATH, "/html/body/app-root/app-tenday/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[2]/section/div[3]/div[1]/div/div[1]/div/lib-forecast-chart/div/div/div/lib-forecast-chart-header-daily/div/div"
                ))
            )
            forecast_text = forecast_data_element.text.splitlines()

            # Parse dates and temperatures from forecast data
            dates, temps = [], []
            date_pattern = r"[A-Za-z]{3} \d{1,2}/\d{1,2}"
            temp_pattern = r"-?\d+° \| -?\d+°C"

            for line in forecast_text:
                if re.match(date_pattern, line):
                    dates.append(line)
                elif re.match(temp_pattern, line):
                    temps.append(line)

            # Debugging output to verify parsed data
            print("Parsed Dates:", dates)
            print("Parsed Temps:", temps)

            # Locate forecast for the target date
            if display_date_str in dates:
                date_index = dates.index(display_date_str)
                if date_index < len(temps):
                    temperature_values = re.findall(r"-?\d+", temps[date_index])
                    if len(temperature_values) >= 2:
                        min_temp, max_temp = map(int, temperature_values[:2])
                        avg_temp = (min_temp + max_temp) // 2
                        csvwriter.writerow([forecast_date_str, max_temp, avg_temp, min_temp])
                        print(f"Forecast for {forecast_date_str} written: Max={max_temp}, Avg={avg_temp}, Min={min_temp}")
                    else:
                        print(f"Temperature values for {display_date_str} are incomplete or malformed.")
                else:
                    print(f"No temperature data found for date index {date_index}")
            else:
                print(f"Forecast for {display_date_str} not found in parsed dates.")

        except TimeoutException:
            print(f"Could not retrieve forecast for {display_date_str}")
        finally:
            driver.quit()
