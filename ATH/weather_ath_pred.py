# !!!!WORKING!!!! Parses 3 following days

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
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException

# Path to your ChromeDriver executable
chrome_driver_path = '/usr/local/bin/chromedriver'

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--start-maximized")

# Get today's date
today = date.today()

# Function to compare dates
def compare_dates(date1, date2):
    return date1 >= date2

# Function to check if a date is the last day of the month
def is_last_day_of_month(date):
    next_date = date.replace(day=date.day + 1)
    return next_date.month != date.month

# Mapping of month abbreviations to their respective numeric values
month_mapping = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

last_date = None  # Ensure it's defined


# Check if the CSV file exists and is not empty
if os.path.isfile('weather_data_ath_pred.csv') and os.path.getsize('weather_data_ath_pred.csv') > 0:
    with open('weather_data_ath_pred.csv', 'r') as csvfile:
        last_date = None
        print("last date is =", last_date)
        for line in csvfile.readlines():
            if line.strip():
                last_date = line.split(',')[0]  # Assuming date is the first column
                print("Last Date =", last_date)

# Initialize start_year with a default value
default_year = 2022
default_month = 1
# start_day = 1
# last_date = None

# Check if last_date is valid
if last_date:
    try:
        last_date_parts = last_date.split('/')  # Split date into parts
        if len(last_date_parts) < 3:  # Check if date is in expected format
            raise ValueError(f"Invalid date format: {last_date}")  # Raise error for invalid format
        last_month = month_mapping[last_date_parts[1]]  # Convert month abbreviation to numeric value
        last_day = int(last_date_parts[2])  # Parse the day part
    except (ValueError, KeyError) as e:  # Catch errors for invalid date format or month abbreviation
        print(f"Error processing last date: {e}")
        last_date = None  # Set last_date to None if there is an issue with it
else:
    print("No valid last date found in the CSV.")

# If last_date is None (or invalid), set the default start month
if not last_date:
    print("Using default start values.")
    start_month = default_month  # Default to January if no valid last_date


# Check if the last date in CSV file is February 27th or 28th
if last_date:
    last_date_parts = last_date.split('/')
    last_month = month_mapping[last_date_parts[1]]  # Convert month abbreviation to numeric value
    last_day = int(last_date_parts[2])
    if is_last_day_of_month(datetime.strptime(last_date, '%Y/%b/%d').date()):
        # If the last date is the last day of the month, set the start month to the next month
        start_month = last_month + 1
        # If the start month exceeds 12, reset it to 1 and increment the year
        if start_month > 12:
            start_month = 1
            start_year = int(last_date_parts[0]) + 1  # Increment the year
    else:
        # If the last date is not the last day of the month, use the last month from the CSV
        start_month = last_month
        start_year = int(last_date_parts[0])

else:
    start_month = default_month

start_year = default_year

# Open the CSV file in append mode
with open('weather_data_ath_pred.csv', 'a', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)

    # If the CSV file is empty, add the header
    if csvfile.tell() == 0:
        csvwriter.writerow(['Date', 'Max', 'Avg', 'Min'])  # Header

    # Iterate over the years from start_year to the current year
    for year in range(start_year, today.year + 1):
        # For the starting year, start from the calculated start_month
        if year == start_year:
            month_range_start = start_month
        else:
            month_range_start = 1

        # For the current year, end at the current month
        if year == today.year:
            month_range_end = today.month
        else:
            month_range_end = 12

        # Iterate over the months for the current year
        for month in range(month_range_start, month_range_end + 1):
            # Construct the URL for the current month and year
            url = f"https://www.wunderground.com/history/monthly/gr/athens/LGAV/date/{year}-{month}"

            # Start a WebDriver and open the webpage
            service = Service(chrome_driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(url)

            # Wait for the cookie consent pop-up iframe to appear (adjust timeout as needed)
            try:
                cookie_popup_iframe = WebDriverWait(driver, 10).until(
                    EC.frame_to_be_available_and_switch_to_it(((By.CSS_SELECTOR, 'iframe[title="SP Consent Message"]')))
                )
                print("Cookie consent pop-up iframe found.")

                try:
                    # Once inside the iframe, locate the accept button
                    accept_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(((By.CSS_SELECTOR, 'button[title="Accept all"]')))
                    )
                    print("Accept button found inside the cookie pop-up iframe.")
                    accept_button.click()

                    # Switch back to the default content
                    driver.switch_to.default_content()

                except Exception as e:
                    print("Couldn't find the accept button inside the cookie pop-up iframe:", e)
            except Exception as e:
                print("No cookie consent pop-up iframe found:", e)

            try:

                # Maximum number of retries
                max_retries = 3
                retry_count = 0

                while retry_count < max_retries:
                    try:
                        try:
                                # Wait for the button to be clickable
                                button = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[id="wuSettings"]' ))
                                )
                                
                                # Click the button
                                button.click()
                                
                                # Wait for all tables to be present on the page
                                tables = WebDriverWait(driver, 10).until(
                                    #EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
                                    EC.presence_of_all_elements_located((By.XPATH,'/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[1]/div[2]/lib-settings/header/div'))
                                )
                        
                                # Wait for all tables to be present on the page
                                tables = WebDriverWait(driver, 10).until(
                                    #EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
                                    EC.presence_of_all_elements_located((By.XPATH,'/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[1]/div[2]/lib-settings/header/div/div/a[2]'))
                                )

                                # Wait for the element to be clickable
                                link_element = WebDriverWait(driver, 20).until(
                                    EC.element_to_be_clickable((By.XPATH,'/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[1]/div[2]/lib-settings/header/div/div/a[2]'))
                                )
                                link_element.click()
                                
                                # # If button click and table presence succeeded, break out of the retry loop
                                #break
                        except StaleElementReferenceException:
                            # Handle stale element reference by locating the element again
                            print("StaleElementReferenceException occurred. Locating elements again...")
                            # You can add code here to locate the elements again and retry the action
                            # Wait for all tables to be present on the page
                            tables = WebDriverWait(driver, 10).until(
                                    #EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
                                    EC.presence_of_all_elements_located((By.XPATH,'/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[1]/div[2]/lib-settings/header/div'))
                                )
                        
                                # Wait for all tables to be present on the page
                            tables = WebDriverWait(driver, 10).until(
                                    #EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
                                    EC.presence_of_all_elements_located((By.XPATH,'/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[1]/div[2]/lib-settings/header/div/div/a[2]'))
                                )
                        # If button click and table presence succeeded, break out of the retry loop
                        break

                    except TimeoutException:
                        # If the button is not clickable within the timeout, increment retry count and wait for a while before retrying
                        retry_count += 1
                        print(f"Retry attempt {retry_count}...")
                        time.sleep(2)  # Wait for 2 seconds before retrying

                # Check if maximum retries reached without success
                if retry_count == max_retries:
                    print("Maximum retries reached. Failed to click the button.")
                    # You can add further actions here, like raising an exception or handling the failure.

                # Wait for all tables to be present on the page
                tables = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
                )

                # Choose the second table from the list of tables
                main_table = tables[1]

                # Find sub tables with attribute aria-labelledby="Days data"
                sub_tables = main_table.find_elements(By.CSS_SELECTOR, 'table[aria-labelledby="Days data"]')

                # Extract and store data from sub tables
                sub_table_data = []
                for sub_table in sub_tables:
                    sub_table_rows = sub_table.find_elements(By.TAG_NAME, 'tr')
                    sub_table_data.append([[column.text.strip() for column in row.find_elements(By.TAG_NAME, 'td')]
                                           for row in sub_table_rows])

                # Transpose sub tables to form columns
                transposed_sub_tables = []
                for i in range(len(sub_table_data[0])):
                    column = []
                    for sub_table in sub_table_data:
                        if i < len(sub_table):
                            column.extend(sub_table[i])
                    transposed_sub_tables.append(column)

                # Write data to CSV
                for idx, row in enumerate(transposed_sub_tables):
                    if idx == 0:
                        current_month = row[0] # Extracting the month from the first row
                        continue # Skip the header row
                    # Construct the date string using the year, month, and day
                    day = int(row[0]) # Assuming the day is always provided as the first element
                    date_str = f'{year}/{current_month}/{day:02}' # Constructing the date string
                    print("date_str = ", date_str)
                    # Replace the first element of the row with the constructed date string
                    row[0] = date_str
                    print("last_date = ", last_date)
                    print("day = ", day)
                    # Write the row to the CSV file only if it's not empty and not equal to the last date
                    if any(row) and (last_date is None or (compare_dates(date_str, last_date) and date_str != last_date)):
                        csvwriter.writerow(row[:4])


            finally:
                # Close the WebDriver
                driver.quit()

            # Stop if the current year and month reach today's date
            if year == today.year and month == today.month:
                break

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

        try:
            # Handle cookie consent popup if present
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
                print("No cookie consent popup:", e)

            # Click on wuSettings button to switch to Celsius
            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                try:
                    wu_settings_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, 'wuSettings'))
                    )
                    wu_settings_button.click()
                    
                    celsius_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="wuSettings-quick"]/div/a[2]'))
                    )
                    celsius_button.click()
                    break  # Exit the retry loop once successful
                except TimeoutException:
                    retry_count += 1
                    print(f"Retry attempt {retry_count} to switch to Celsius...")
                    time.sleep(2)
                except StaleElementReferenceException:
                            # Handle stale element reference by locating the element again
                            print("StaleElementReferenceException occurred. Locating elements again...")
                            # You can add code here to locate the elements again and retry the action
                            # Wait for all tables to be present on the page


            # Wait for the forecast table to load fully
            forecast_table = WebDriverWait(driver, 20).until(
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


# import csv
# import os
# import re
# import time
# from datetime import date, datetime, timedelta
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import TimeoutException

# # Path to your ChromeDriver executable
# chrome_driver_path = '/usr/local/bin/chromedriver'

# # Chrome options
# chrome_options = Options()
# chrome_options.add_argument("--start-maximized")

# # Today's date
# today = date.today()

# # Check if CSV exists and load existing dates
# csv_file_path = 'weather_data_ath_pred.csv'
# existing_dates = set()
# last_date = None

# if os.path.isfile(csv_file_path) and os.path.getsize(csv_file_path) > 0:
#     with open(csv_file_path, 'r') as csvfile:
#         reader = csv.reader(csvfile)
#         next(reader, None)  # Skip the header row
#         for line in reader:
#             if line:
#                 date_str = line[0]  # Date in first column
#                 existing_dates.add(date_str)
#                 last_date = date_str  # Track the last date found in CSV

# # Determine if historical data collection is needed
# go_to_forecast = (last_date == today.strftime('%Y/%b/%d'))

# # Open the CSV file in append mode
# with open(csv_file_path, 'a', newline='') as csvfile:
#     csvwriter = csv.writer(csvfile)

#     # Add CSV header if it's a new file
#     if os.path.getsize(csv_file_path) == 0:
#         csvwriter.writerow(['Date', 'Max', 'Avg', 'Min'])  # Header

#     # Forecast Section for the next 3 days
#     for day in range(1, 4):
#         forecast_date = today + timedelta(days=day)
#         forecast_date_str = forecast_date.strftime('%Y/%b/%d')  # For CSV format
#         display_date_str = forecast_date.strftime('%a %m/%d')  # For website display

#         # Open forecast page
#         forecast_url = "https://www.wunderground.com/forecast/gr/athens"
#         service = Service(chrome_driver_path)
#         driver = webdriver.Chrome(service=service, options=chrome_options)
#         driver.get(forecast_url)

#         # max_retries = 3
#         # retry_count = 0
        
#         try:
#             # Handle cookie consent popup if present
#             try:
#                 cookie_popup_iframe = WebDriverWait(driver, 10).until(
#                     EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe[title="SP Consent Message"]'))
#                 )
#                 accept_button = WebDriverWait(driver, 20).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Accept all"]'))
#                 )
#                 accept_button.click()



#                 driver.switch_to.default_content()

#                 button = WebDriverWait(driver, 10).until(
#                         EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[id="wuSettings"]'))
#                     )
#                 button.click()

#                     # Wait for forecast data
#                 WebDriverWait(driver, 10).until(
#                     EC.presence_of_all_element_located((By.XPATH, "//div[contains(@class, 'obs-date')]"))
#                 )

#                 # Retrieve forecast data
#                 forecast_data_element = WebDriverWait(driver, 10).until(
#                     EC.presence_of_all_element_located((
#                         By.XPATH, "/html/body/app-root/app-tenday/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[2]/section/div[3]/div[1]/div/div[1]/div/lib-forecast-chart/div/div/div/lib-forecast-chart-header-daily/div/div"
#                     ))
#                 )


#                 link_element = WebDriverWait(driver, 10).until(
#                         EC.element_to_be_clickable((By.XPATH, '//*[@id="wuSettings-quick"]/div/a[2]'))
#                     )
#                 link_element.click()
#                 break

#             except Exception as e:
#                 print("No cookie consent popup:", e)


#             # Wait for forecast data
#             WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'obs-date')]"))
#             )

#             # Retrieve forecast data
#             forecast_data_element = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((
#                     By.XPATH, "/html/body/app-root/app-tenday/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[2]/section/div[3]/div[1]/div/div[1]/div/lib-forecast-chart/div/div/div/lib-forecast-chart-header-daily/div/div"
#                 ))
#             )
#             forecast_text = forecast_data_element.text.splitlines()

#             # Parse dates and temperatures from forecast data
#             dates, temps = [], []
#             date_pattern = r"[A-Za-z]{3} \d{1,2}/\d{1,2}"
#             temp_pattern = r"-?\d+° \| -?\d+°C"

#             for line in forecast_text:
#                 if re.match(date_pattern, line):
#                     dates.append(line)
#                 elif re.match(temp_pattern, line):
#                     temps.append(line)

#             # Debugging output to verify parsed data
#             print("Parsed Dates:", dates)
#             print("Parsed Temps:", temps)

#             # Locate forecast for the target date
#             if display_date_str in dates:
#                 date_index = dates.index(display_date_str)
#                 if date_index < len(temps):
#                     temperature_values = re.findall(r"-?\d+", temps[date_index])
#                     if len(temperature_values) >= 2:
#                         min_temp, max_temp = map(int, temperature_values[:2])
#                         avg_temp = (min_temp + max_temp) // 2
#                         csvwriter.writerow([forecast_date_str, max_temp, avg_temp, min_temp])
#                         print(f"Forecast for {forecast_date_str} written: Max={max_temp}, Avg={avg_temp}, Min={min_temp}")
#                     else:
#                         print(f"Temperature values for {display_date_str} are incomplete or malformed.")
#                 else:
#                     print(f"No temperature data found for date index {date_index}")
#             else:
#                 print(f"Forecast for {display_date_str} not found in parsed dates.")

#         except TimeoutException:
#             print(f"Could not retrieve forecast for {display_date_str}")
#         finally:
#             driver.quit()



# import csv
# import os
# import re
# from datetime import date, timedelta
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import TimeoutException

# # Path to your ChromeDriver executable
# chrome_driver_path = '/usr/local/bin/chromedriver'

# # Set up Chrome options
# chrome_options = Options()
# chrome_options.add_argument("--start-maximized")

# # Today's date
# today = date.today()

# # CSV file path
# csv_file_path = 'weather_data_ath_pred.csv'

# # Check if the CSV file exists and create a header if it doesn't
# if not os.path.isfile(csv_file_path) or os.path.getsize(csv_file_path) == 0:
#     with open(csv_file_path, 'w', newline='') as csvfile:
#         csvwriter = csv.writer(csvfile)
#         csvwriter.writerow(['Date', 'Max', 'Avg', 'Min'])  # Header

# # Open the CSV file in append mode
# with open(csv_file_path, 'a', newline='') as csvfile:
#     csvwriter = csv.writer(csvfile)

#     # Loop to fetch forecast for the next 3 days
#     for day in range(1, 4):  # Next 3 days
#         forecast_date = today + timedelta(days=day)
#         forecast_date_str = forecast_date.strftime('%Y/%b/%d')  # Format for CSV
#         display_date_str = forecast_date.strftime('%a %m/%d')  # Format for site display

#         # URL for the forecast page
#         forecast_url = "https://www.wunderground.com/forecast/gr/athens"
        
#         # Initialize WebDriver
#         service = Service(chrome_driver_path)
#         driver = webdriver.Chrome(service=service, options=chrome_options)
#         driver.get(forecast_url)

#         try:
#             # Wait for cookie consent popup, if present, and dismiss it
#             try:
#                 cookie_popup_iframe = WebDriverWait(driver, 10).until(
#                     EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe[title="SP Consent Message"]'))
#                 )
#                 accept_button = WebDriverWait(driver, 10).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Accept all"]'))
#                 )
#                 accept_button.click()
#                 driver.switch_to.default_content()
#             except Exception as e:
#                 print("No cookie consent popup found:", e)

#             # Wait until forecast data is loaded
#             WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'obs-date')]"))
#             )

#             # Locate forecast data
#             forecast_data_element = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((
#                     By.XPATH, "/html/body/app-root/app-tenday/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[2]/section/div[3]/div[1]/div/div[1]/div/lib-forecast-chart/div/div/div/lib-forecast-chart-header-daily/div/div"
#                 ))
#             )
#             forecast_text = forecast_data_element.text.splitlines()

#             # Lists to store data
#             dates, temps = [], []
#             date_pattern = r"[A-Za-z]{3} \d{1,2}/\d{1,2}"
#             temp_pattern = r"-?\d+° \| -?\d+°C"

#             # Parse the forecast data for dates and temps
#             for line in forecast_text:
#                 if re.match(date_pattern, line):
#                     dates.append(line)
#                 elif re.match(temp_pattern, line):
#                     temps.append(line)

#             # Locate and write the forecast for the target date
#             if display_date_str in dates:
#                 date_index = dates.index(display_date_str)
#                 temperature_values = re.findall(r"-?\d+", temps[date_index])
                
#                 # Ensure exactly two temperature values
#                 if len(temperature_values) == 2:
#                     min_temp, max_temp = map(int, temperature_values)
#                     avg_temp = (min_temp + max_temp) // 2
#                     csvwriter.writerow([forecast_date_str, max_temp, avg_temp, min_temp])
#                     print(f"Forecast written to CSV for {forecast_date_str}: Max={max_temp}, Avg={avg_temp}, Min={min_temp}")
#                 else:
#                     print(f"Unexpected temperature format for {display_date_str}: {temps[date_index]}")
#             else:
#                 print(f"Forecast for {display_date_str} not found.")

#         except TimeoutException:
#             print(f"Could not retrieve forecast data for {display_date_str}")
#         finally:
#             driver.quit()


# import csv, os, time
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# from datetime import date, datetime, timedelta
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# import re

# # Path to your ChromeDriver executable
# chrome_driver_path = '/usr/local/bin/chromedriver'

# chrome_options = Options()
# chrome_options.add_argument("--start-maximized")

# # Get today's date
# today = date.today()

# # Function to parse and compare dates
# def parse_date(date_str):
#     return datetime.strptime(date_str, '%Y/%b/%d').date()

# # Check if the CSV file exists and load existing dates into a set
# existing_dates = set()
# last_date = None

# if os.path.isfile('weather_data_ath_pred.csv') and os.path.getsize('weather_data_ath_pred.csv') > 0:
#     with open('weather_data_ath_pred.csv', 'r') as csvfile:
#         reader = csv.reader(csvfile)
#         next(reader, None)  # Skip the header row
#         for line in reader:
#             if line:
#                 date_str = line[0]  # Assuming date is the first column
#                 existing_dates.add(date_str)
#                 last_date = date_str  # Track the last date found in CSV
#                 print("Last Date =", last_date)

# # If last_date exists and matches today's date, go directly to the forecast section
# if last_date == today.strftime('%Y/%b/%d'):
#     go_to_forecast = True
# else:
#     go_to_forecast = False

# # Open the CSV file in append mode
# with open('weather_data_ath_pred.csv', 'a', newline='') as csvfile:
#     csvwriter = csv.writer(csvfile)

#     # If the CSV file is empty, add the header
#     if csvfile.tell() == 0:
#         csvwriter.writerow(['Date', 'Max', 'Avg', 'Min'])  # Header

#     # Historical data section: Only execute if today’s data isn't in the CSV
#     if not go_to_forecast:
#         # Variables to define the start point
#         start_year = today.year
#         start_month = today.month

#         # Iterate over the months from start_month to the current month
#         for year in range(start_year, today.year + 1):
#             month_range_start = start_month if year == start_year else 1
#             month_range_end = today.month if year == today.year else 12

#             # Iterate over the months for the current year
#             for month in range(month_range_start, month_range_end + 1):
#                 url = f"https://www.wunderground.com/history/monthly/gr/athens/LGAV/date/{year}-{month}"

#                 # Start a WebDriver and open the webpage
#                 service = Service(chrome_driver_path)
#                 driver = webdriver.Chrome(service=service, options=chrome_options)
#                 driver.get(url)

#                 try:
#                     cookie_popup_iframe = WebDriverWait(driver, 10).until(
#                         EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe[title="SP Consent Message"]'))
#                     )
#                     accept_button = WebDriverWait(driver, 10).until(
#                         EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Accept all"]'))
#                     )
#                     accept_button.click()
#                     driver.switch_to.default_content()
#                 except Exception as e:
#                     print("No cookie consent pop-up iframe found:", e)

#                 # Retry logic to handle potential stale or timeout issues for forecast data
#                 retry_count = 0
#                 max_retries = 3
#                 while retry_count < max_retries:
#                     try:
#                         button = WebDriverWait(driver, 10).until(
#                             EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[id="wuSettings"]'))
#                         )
#                         button.click()
#                         link_element = WebDriverWait(driver, 20).until(
#                             EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[1]/div[2]/lib-settings/header/div/div/a[2]'))
#                         )
#                         link_element.click()
#                         break
#                     except TimeoutException:
#                         retry_count += 1
#                         print(f"Retry attempt {retry_count}...")
#                         time.sleep(2)

#                 # Assuming the historical data is gathered, switch to forecast section if needed
#                 if retry_count == max_retries:
#                     print("Maximum retries reached. Failed to click the button.")
#         else:
#             driver.quit()

# # Forecast section for the next 3 days
# with open('weather_data_ath_pred.csv', 'a', newline='') as csvfile:
#     csvwriter = csv.writer(csvfile)

#     for day in range(1, 4):  # Loop to forecast for the next 3 days
#         forecast_date = today + timedelta(days=day)
#         forecast_date_str = forecast_date.strftime('%Y/%b/%d')  # For CSV format
#         display_date_str = forecast_date.strftime('%a %m/%d')  # For website display

#         # Open the forecast page
#         forecast_url = "https://www.wunderground.com/forecast/gr/athens"
#         service = Service(chrome_driver_path)
#         driver = webdriver.Chrome(service=service, options=chrome_options)
#         driver.get(forecast_url)

#         try:
#             # Wait for forecast data element
#             WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'obs-date')]"))
#             )

#             # Retrieve and parse forecast data
#             forecast_data_element = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((
#                     By.XPATH, "/html/body/app-root/app-tenday/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[2]/section/div[3]/div[1]/div/div[1]/div/lib-forecast-chart/div/div/div/lib-forecast-chart-header-daily/div/div"
#                 ))
#             )
#             forecast_text = forecast_data_element.text.splitlines()

#             # Lists to store data
#             dates, temps, conditions, precipitation = [], [], [], []
#             date_pattern = r"[A-Za-z]{3} \d{1,2}/\d{1,2}"
#             temp_pattern = r"-?\d+° \| -?\d+°C"

#             # Parse the forecast data
#             for line in forecast_text:
#                 if re.match(date_pattern, line):
#                     dates.append(line)
#                 elif re.match(temp_pattern, line):
#                     temps.append(line)

#             # Locate and write the forecast for the target date
#             if display_date_str in dates:
#                 date_index = dates.index(display_date_str)
#                 min_temp, max_temp = map(int, re.findall(r"-?\d+", temps[date_index]))
#                 avg_temp = (min_temp + max_temp) // 2
#                 csvwriter.writerow([forecast_date_str, max_temp, avg_temp, min_temp])
#                 print(f"Forecast written to CSV for {forecast_date_str}: {max_temp}, {avg_temp}, {min_temp}")
#             else:
#                 print(f"Forecast for {display_date_str} not found.")

#         except TimeoutException:
#             print(f"Could not retrieve forecast for {display_date_str}")
#         finally:
#             driver.quit()



# # WORKING -> forecasting works for 1 day

# import csv, os, time
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# from datetime import date, datetime, timedelta
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
# import re

# # Path to your ChromeDriver executable
# chrome_driver_path = '/usr/local/bin/chromedriver'

# chrome_options = Options()
# chrome_options.add_argument("--start-maximized")

# # Get today's date
# today = date.today()

# # Function to parse and compare dates
# def parse_date(date_str):
#     return datetime.strptime(date_str, '%Y/%b/%d').date()

# # Function to check if a date is the last day of the month
# def is_last_day_of_month(date):
#     next_date = date + timedelta(days=1)
#     return next_date.month != date.month

# # Check if the CSV file exists and load existing dates into a set
# existing_dates = set()
# last_date = None

# if os.path.isfile('weather_data_ath_pred.csv') and os.path.getsize('weather_data_ath_pred.csv') > 0:
#     with open('weather_data_ath_pred.csv', 'r') as csvfile:
#         reader = csv.reader(csvfile)
#         next(reader, None)  # Skip the header row
#         for line in reader:
#             if line:
#                 date_str = line[0]  # Assuming date is the first column
#                 existing_dates.add(date_str)
#                 last_date = date_str  # Track the last date found in CSV
#                 print("Last Date =", last_date)

# # Check if last_date is today's date
# if last_date == today.strftime('%Y/%b/%d'):
#     print("Last date is today's date. Proceeding to weather forecast section...")
# else:
#     # Variables to define the start point
#     start_year = 2024  # Default year
#     start_month = 11   # Default month

#     # If last_date exists, update start_year and start_month accordingly
#     if last_date:
#         last_date_obj = parse_date(last_date)
#         start_year = last_date_obj.year
#         start_month = last_date_obj.month + 1 if is_last_day_of_month(last_date_obj) else last_date_obj.month
#         if start_month > 12:
#             start_month = 1
#             start_year += 1

#     # Open the CSV file in append mode
#     with open('weather_data_ath_pred.csv', 'a', newline='') as csvfile:
#         csvwriter = csv.writer(csvfile)

#         # If the CSV file is empty, add the header
#         if csvfile.tell() == 0:
#             csvwriter.writerow(['Date', 'Max', 'Avg', 'Min'])  # Header

#         # Iterate over the years from start_year to the current year
#         for year in range(start_year, today.year + 1):
#             month_range_start = start_month if year == start_year else 1
#             month_range_end = today.month if year == today.year else 12

#             # Iterate over the months for the current year
#             for month in range(month_range_start, month_range_end + 1):
#                 url = f"https://www.wunderground.com/history/monthly/gr/athens/LGAV/date/{year}-{month}"

#                 # Start a WebDriver and open the webpage
#                 service = Service(chrome_driver_path)
#                 driver = webdriver.Chrome(service=service, options=chrome_options)
#                 driver.get(url)

#                 try:
#                     cookie_popup_iframe = WebDriverWait(driver, 10).until(
#                         EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe[title="SP Consent Message"]'))
#                     )
#                     accept_button = WebDriverWait(driver, 10).until(
#                         EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Accept all"]'))
#                     )
#                     accept_button.click()
#                     driver.switch_to.default_content()
#                 except Exception as e:
#                     print("No cookie consent pop-up iframe found:", e)

#                 try:
#                     max_retries = 3
#                     retry_count = 0

#                     while retry_count < max_retries:
#                         try:
#                             button = WebDriverWait(driver, 10).until(
#                                 EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[id="wuSettings"]'))
#                             )
#                             button.click()
#                             link_element = WebDriverWait(driver, 20).until(
#                                 EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[1]/div[2]/lib-settings/header/div/div/a[2]'))
#                             )
#                             link_element.click()
#                             break
#                         except TimeoutException:
#                             retry_count += 1
#                             print(f"Retry attempt {retry_count}...")
#                             time.sleep(2)

#                     if retry_count == max_retries:
#                         print("Maximum retries reached. Failed to click the button.")

#                     tables = WebDriverWait(driver, 10).until(
#                         EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
#                     )

#                     main_table = tables[1]
#                     sub_tables = main_table.find_elements(By.CSS_SELECTOR, 'table[aria-labelledby="Days data"]')

#                     sub_table_data = []
#                     for sub_table in sub_tables:
#                         sub_table_rows = sub_table.find_elements(By.TAG_NAME, 'tr')
#                         sub_table_data.append([[column.text.strip() for column in row.find_elements(By.TAG_NAME, 'td')]
#                                                for row in sub_table_rows])

#                     transposed_sub_tables = []
#                     for i in range(len(sub_table_data[0])):
#                         column = []
#                         for sub_table in sub_table_data:
#                             if i < len(sub_table):
#                                 column.extend(sub_table[i])
#                         transposed_sub_tables.append(column)

#                     for idx, row in enumerate(transposed_sub_tables):
#                         if idx == 0:
#                             current_month = row[0]
#                             continue
#                         day = int(row[0])
#                         date_str = f'{year}/{current_month}/{day:02}'
#                         row[0] = date_str
#                         print(f"Processing date: {date_str}")

#                         if any(row) and date_str not in existing_dates and date_str <= today.strftime('%Y/%b/%d'):
#                             csvwriter.writerow(row[:4])
#                             existing_dates.add(date_str)
#                             print(f"Written to CSV: {row[:4]}")

#                         # Check if we've reached today's date
#                         if date_str == today.strftime('%Y/%b/%d'):
#                             print("Reached today's date in historical data. Switching to forecast section...")
#                             driver.quit()
#                             goto_forecast_section = True
#                             break
#                     else:
#                         continue
#                     break

#                 finally:
#                     driver.quit()


# # Path to your ChromeDriver executable
# chrome_driver_path = '/usr/local/bin/chromedriver'

# chrome_options = Options()
# chrome_options.add_argument("--start-maximized")

# # Get today's date
# today = date.today()

# # Function to parse and compare dates
# def parse_date(date_str):
#     return datetime.strptime(date_str, '%Y/%b/%d').date()

# # Check if the CSV file exists and load existing dates into a set
# existing_dates = set()
# last_date = None

# if os.path.isfile('weather_data_ath_pred.csv') and os.path.getsize('weather_data_ath_pred.csv') > 0:
#     with open('weather_data_ath_pred.csv', 'r') as csvfile:
#         reader = csv.reader(csvfile)
#         next(reader, None)  # Skip the header row
#         for line in reader:
#             if line:
#                 date_str = line[0]  # Assuming date is the first column
#                 existing_dates.add(date_str)
#                 last_date = date_str  # Track the last date found in CSV
#                 print("Last Date =", last_date)

# # If last_date exists and matches today's date, go directly to the forecast section
# if last_date == today.strftime('%Y/%b/%d'):
#     go_to_forecast = True
# else:
#     go_to_forecast = False

# # Open the CSV file in append mode
# with open('weather_data_ath_pred.csv', 'a', newline='') as csvfile:
#     csvwriter = csv.writer(csvfile)

#     # If the CSV file is empty, add the header
#     if csvfile.tell() == 0:
#         csvwriter.writerow(['Date', 'Max', 'Avg', 'Min'])  # Header

#     # Historical data section: Only execute if today’s data isn't in the CSV
#     if not go_to_forecast:
#         # Variables to define the start point
#         start_year = today.year
#         start_month = today.month

#         # Iterate over the months from start_month to the current month
#         for year in range(start_year, today.year + 1):
#             month_range_start = start_month if year == start_year else 1
#             month_range_end = today.month if year == today.year else 12

#             # Iterate over the months for the current year
#             for month in range(month_range_start, month_range_end + 1):
#                 url = f"https://www.wunderground.com/history/monthly/gr/athens/LGAV/date/{year}-{month}"

#                 # Start a WebDriver and open the webpage
#                 service = Service(chrome_driver_path)
#                 driver = webdriver.Chrome(service=service, options=chrome_options)
#                 driver.get(url)
#                 max_retries = 3
#                 retry_count = 0
                
#                 try:
#                     cookie_popup_iframe = WebDriverWait(driver, 10).until(
#                         EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe[title="SP Consent Message"]'))
#                     )
#                     accept_button = WebDriverWait(driver, 10).until(
#                         EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Accept all"]'))
#                     )
#                     accept_button.click()
#                     driver.switch_to.default_content()
#                 except Exception as e:
#                     print("No cookie consent pop-up iframe found or handled:", e)
                
#                 # Retry logic with improved error handling for wuSettings button click
#                 retry_count = 0
#                 max_retries = 3

#                 while retry_count < max_retries:
#                     try:
#                         # Locate and click the wuSettings button
#                         button = WebDriverWait(driver, 15).until(
#                             EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[id="wuSettings"]'))
#                         )
#                         driver.execute_script("arguments[0].scrollIntoView();", button)  # Ensure button is in view
#                         button.click()

#                         # Attempt to locate the link element after clicking wuSettings
#                         link_element = WebDriverWait(driver, 20).until(
#                             EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/app-tenday/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[1]/div[2]/lib-settings'))
#                         )
#                         link_element.click()
#                         break  # Exit the loop if successful

#                     except StaleElementReferenceException:
#                         # Refresh the reference by retrying
#                         print("Encountered StaleElementReferenceException, retrying...")
#                         retry_count += 1
#                         time.sleep(1)
                        
#                     except TimeoutException:
#                         # If element still not clickable, retry
#                         retry_count += 1
#                         print(f"Retry attempt {retry_count} due to TimeoutException...")
#                         time.sleep(2)

#                     except NoSuchElementException:
#                         print("The element was not found in the DOM.")
#                         break

#                 if retry_count == max_retries:
#                     print("Maximum retries reached. Failed to click the wuSettings button or link element.")


#     # Forecast section for the next day
#     if last_date == today.strftime('%Y/%b/%d'):
#         # Calculate tomorrow's date
#         tomorrow = today + timedelta(days=1)
#         tomorrow_str = tomorrow.strftime('%a %m/%d')  # Format to match displayed date on the website
#         formatted_tomorrow_date = tomorrow.strftime('%Y/%b/%d')  # Format for the CSV

#         # Open the forecast page
#         forecast_url = "https://www.wunderground.com/forecast/gr/athens"
#         service = Service(chrome_driver_path)
#         driver = webdriver.Chrome(service=service, options=chrome_options)
#         driver.get(forecast_url)
#         max_retries = 3
#         retry_count = 0
#         #try:

#         try:
#                     cookie_popup_iframe = WebDriverWait(driver, 10).until(
#                         EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe[title="SP Consent Message"]'))
#                     )
#                     accept_button = WebDriverWait(driver, 10).until(
#                         EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Accept all"]'))
#                     )
#                     accept_button.click()
#                     driver.switch_to.default_content()
#         except Exception as e:
#                     print("No cookie consent pop-up iframe found:", e)
        
#         while retry_count < max_retries:

#                         try:
                            
#                             button = WebDriverWait(driver, 10).until(
#                                 EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[id="wuSettings"]'))
#                             )
#                             button.click()
#                             link_element = WebDriverWait(driver, 10).until(
#                                 EC.element_to_be_clickable((By.XPATH, '//*[@id="wuSettings-quick"]/div/a[2]'))
#                             )
#                             link_element.click()
#                             break
#                         except TimeoutException:
#                             retry_count += 1
#                             print(f"Retry attempt {retry_count}...")
#                             time.sleep(2)


# # Define a delay function to wait until a specific element confirms that the page is fully loaded
# def wait_for_page_load(driver, timeout=20):
#     try:
#         # Wait for an element that signifies the page has fully loaded (e.g., the forecast table header or any key element)
#         WebDriverWait(driver, timeout).until(
#             EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'obs-date')]"))
#         )
#     except TimeoutException:
#         print("Timeout waiting for page to load.")

# # Call the delay function to ensure the page loads fully
# wait_for_page_load(driver)

# # Calculate tomorrow's date in the format displayed on the site
# today = datetime.now()
# tomorrow_str = (today + timedelta(days=1)).strftime('%a %m/%d')
# formatted_date = (today + timedelta(days=1)).strftime('%Y/%b/%d')

# try:
#     # Locate the forecast data element using the full XPath provided
#     forecast_data_element = WebDriverWait(driver, 20).until(
#         EC.presence_of_element_located((
#             By.XPATH, "/html/body/app-root/app-tenday/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[2]/section/div[3]/div[1]/div/div[1]/div/lib-forecast-chart/div/div/div/lib-forecast-chart-header-daily/div/div"
#         ))
#     )

#     # Retrieve the text content and split it into lines
#     forecast_text = forecast_data_element.text.splitlines()
    
#     # Define lists to hold forecast information
#     dates, temps, conditions, precipitation = [], [], [], []
    
#     # Patterns to classify forecast data
#     date_pattern = r"[A-Za-z]{3} \d{1,2}/\d{1,2}"
#     temp_pattern = r"-?\d+° \| -?\d+°C"
#     precip_pattern = r"\d+(\.\d+)? mm"

#     # Iterate through each line and classify the data into lists
#     for line in forecast_text:
#         if re.match(date_pattern, line):
#             dates.append(line)
#         elif re.match(temp_pattern, line):
#             temps.append(line)
#         elif re.match(precip_pattern, line):
#             precipitation.append(line)
#         elif line:  # Remaining lines are conditions
#             conditions.append(line)

#     # Display forecast data in table format
#     print("Dates:        ", ", ".join(dates))
#     print("Temperatures: ", ", ".join(temps))
#     print("Conditions:   ", ", ".join(conditions))
#     print("Precipitation:", ", ".join(precipitation))

#     # Check if tomorrow's date is in the forecast dates
#     if tomorrow_str in dates:
#         # Find the index of tomorrow's date
#         date_index = dates.index(tomorrow_str)
        
#         # Extract temperature values and calculate the average
#         min_temp, max_temp = map(int, re.findall(r"-?\d+", temps[date_index]))
#         avg_temp = (min_temp + max_temp) // 2
        
#         # Output in the requested format
#         print(f"Forecast for {formatted_date}: {min_temp},{avg_temp},{max_temp}")
#     else:
#         print(f"{tomorrow_str} not found in the forecast data.")
        
#         # Fallback to the first available date if tomorrow's forecast is not found
#         if dates:
#             min_temp, max_temp = map(int, re.findall(r"-?\d+", temps[0]))
#             avg_temp = (min_temp + max_temp) // 2
#             print(f"Next available forecast: {formatted_date},{min_temp},{avg_temp},{max_temp}")

# except TimeoutException:
#     print(f"TimeoutException: Could not locate the forecast data for {tomorrow_str}.")
# except NoSuchElementException:
#     print(f"NoSuchElementException: Forecast data element not found.")
# except StaleElementReferenceException:
#     print("Encountered StaleElementReferenceException, retrying...")

# finally:
#     # Close the driver
#     driver.quit()