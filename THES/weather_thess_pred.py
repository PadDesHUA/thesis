
#Version 2 to handle cookies and temperature


import csv
import os
import re
from datetime import date, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# Path to your ChromeDriver executable
chrome_driver_path = '/usr/local/bin/chromedriver'

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Today's date
today = date.today()

# CSV file path
csv_file_path = 'weather_data_ath_pred.csv'

# Check if the CSV file exists and create a header if it doesn't
if not os.path.isfile(csv_file_path) or os.path.getsize(csv_file_path) == 0:
    with open(csv_file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Date', 'Max', 'Avg', 'Min'])  # Header

# Open the CSV file in append mode
with open(csv_file_path, 'a', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)

    # Loop to fetch forecast for the next 3 days
    for day in range(1, 4):  # Next 3 days
        forecast_date = today + timedelta(days=day)
        forecast_date_str = forecast_date.strftime('%Y/%b/%d')  # Format for CSV
        display_date_str = forecast_date.strftime('%a %m/%d')  # Format for site display

        # URL for the forecast page
        forecast_url = "https://www.wunderground.com/forecast/gr/athens"
        
        # Initialize WebDriver
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(forecast_url)

        try:
            # Wait for cookie consent popup, if present, and dismiss it
            try:
                cookie_popup_iframe = WebDriverWait(driver, 10).until(
                    EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe[title="SP Consent Message"]'))
                )
                accept_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Accept all"]'))
                )
                accept_button.click()
                driver.switch_to.default_content()
            except Exception as e:
                print("No cookie consent popup found:", e)

            # Wait until forecast data is loaded
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'obs-date')]"))
            )

            # Locate forecast data
            forecast_data_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((
                    By.XPATH, "/html/body/app-root/app-tenday/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[2]/section/div[3]/div[1]/div/div[1]/div/lib-forecast-chart/div/div/div/lib-forecast-chart-header-daily/div/div"
                ))
            )
            forecast_text = forecast_data_element.text.splitlines()

            # Lists to store data
            dates, temps = [], []
            date_pattern = r"[A-Za-z]{3} \d{1,2}/\d{1,2}"
            temp_pattern = r"-?\d+° \| -?\d+°C"

            # Parse the forecast data for dates and temps
            for line in forecast_text:
                if re.match(date_pattern, line):
                    dates.append(line)
                elif re.match(temp_pattern, line):
                    temps.append(line)

            # Locate and write the forecast for the target date
            if display_date_str in dates:
                date_index = dates.index(display_date_str)
                temperature_values = re.findall(r"-?\d+", temps[date_index])
                
                # Ensure exactly two temperature values
                if len(temperature_values) == 2:
                    min_temp, max_temp = map(int, temperature_values)
                    avg_temp = (min_temp + max_temp) // 2
                    csvwriter.writerow([forecast_date_str, max_temp, avg_temp, min_temp])
                    print(f"Forecast written to CSV for {forecast_date_str}: Max={max_temp}, Avg={avg_temp}, Min={min_temp}")
                else:
                    print(f"Unexpected temperature format for {display_date_str}: {temps[date_index]}")
            else:
                print(f"Forecast for {display_date_str} not found.")

        except TimeoutException:
            print(f"Could not retrieve forecast data for {display_date_str}")
        finally:
            driver.quit()
