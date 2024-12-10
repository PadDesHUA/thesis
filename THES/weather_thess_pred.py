
#Version to handle cookies and temperature

import csv, os, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import date, datetime, timedelta
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

# Path to your ChromeDriver executable
chrome_driver_path = '/usr/local/bin/chromedriver'

chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Get today's date
today = date.today()

# Function to parse and compare dates
def parse_date(date_str):
    return datetime.strptime(date_str, '%Y/%b/%d').date()

# Check if the CSV file exists and load existing dates into a set
existing_dates = set()
last_date = None

if os.path.isfile('weather_data_ath_pred.csv') and os.path.getsize('weather_data_ath_pred.csv') > 0:
    with open('weather_data_ath_pred.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # Skip the header row
        for line in reader:
            if line:
                date_str = line[0]  # Assuming date is the first column
                existing_dates.add(date_str)
                last_date = date_str  # Track the last date found in CSV
                print("Last Date =", last_date)

# If last_date exists and matches today's date, go directly to the forecast section
if last_date == today.strftime('%Y/%b/%d'):
    go_to_forecast = True
else:
    go_to_forecast = False

# Open the CSV file in append mode
with open('weather_data_ath_pred.csv', 'a', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)

    # If the CSV file is empty, add the header
    if csvfile.tell() == 0:
        csvwriter.writerow(['Date', 'Max', 'Avg', 'Min'])  # Header

    # Historical data section: Only execute if today’s data isn't in the CSV
    if not go_to_forecast:
        # Variables to define the start point
        start_year = today.year
        start_month = today.month

        # Iterate over the months from start_month to the current month
        for year in range(start_year, today.year + 1):
            month_range_start = start_month if year == start_year else 1
            month_range_end = today.month if year == today.year else 12

            # Iterate over the months for the current year
            for month in range(month_range_start, month_range_end + 1):
                url = f"https://www.wunderground.com/history/monthly/gr/athens/LGAV/date/{year}-{month}"

                # Start a WebDriver and open the webpage
                service = Service(chrome_driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.get(url)

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
                    print("No cookie consent pop-up iframe found:", e)

                # Retry logic to handle potential stale or timeout issues for forecast data
                retry_count = 0
                max_retries = 3
                while retry_count < max_retries:
                    try:
                        button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[id="wuSettings"]'))
                        )
                        button.click()
                        link_element = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[1]/div[2]/lib-settings/header/div/div/a[2]'))
                        )
                        link_element.click()
                        break
                    except TimeoutException:
                        retry_count += 1
                        print(f"Retry attempt {retry_count}...")
                        time.sleep(2)

                # Assuming the historical data is gathered, switch to forecast section if needed
                if retry_count == max_retries:
                    print("Maximum retries reached. Failed to click the button.")
        else:
            driver.quit()

# Forecast section for the next 3 days
with open('weather_data_ath_pred.csv', 'a', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)

    for day in range(1, 4):  # Loop to forecast for the next 3 days
        forecast_date = today + timedelta(days=day)
        forecast_date_str = forecast_date.strftime('%Y/%b/%d')  # For CSV format
        display_date_str = forecast_date.strftime('%a %m/%d')  # For website display

        # Open the forecast page
        forecast_url = "https://www.wunderground.com/forecast/gr/athens"
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(forecast_url)

        try:
            # Wait for forecast data element
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'obs-date')]"))
            )

            # Retrieve and parse forecast data
            forecast_data_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((
                    By.XPATH, "/html/body/app-root/app-tenday/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[2]/section/div[3]/div[1]/div/div[1]/div/lib-forecast-chart/div/div/div/lib-forecast-chart-header-daily/div/div"
                ))
            )
            forecast_text = forecast_data_element.text.splitlines()

            # Lists to store data
            dates, temps, conditions, precipitation = [], [], [], []
            date_pattern = r"[A-Za-z]{3} \d{1,2}/\d{1,2}"
            temp_pattern = r"-?\d+° \| -?\d+°C"

            # Parse the forecast data
            for line in forecast_text:
                if re.match(date_pattern, line):
                    dates.append(line)
                elif re.match(temp_pattern, line):
                    temps.append(line)

            # Locate and write the forecast for the target date
            if display_date_str in dates:
                date_index = dates.index(display_date_str)
                min_temp, max_temp = map(int, re.findall(r"-?\d+", temps[date_index]))
                avg_temp = (min_temp + max_temp) // 2
                csvwriter.writerow([forecast_date_str, max_temp, avg_temp, min_temp])
                print(f"Forecast written to CSV for {forecast_date_str}: {max_temp}, {avg_temp}, {min_temp}")
            else:
                print(f"Forecast for {display_date_str} not found.")

        except TimeoutException:
            print(f"Could not retrieve forecast for {display_date_str}")
        finally:
            driver.quit()

