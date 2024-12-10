
# WORKING -> forecasting works for 1 day

import csv, os, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import date, datetime, timedelta
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
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

# Function to check if a date is the last day of the month
def is_last_day_of_month(date):
    next_date = date + timedelta(days=1)
    return next_date.month != date.month

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

# Check if last_date is today's date
if last_date == today.strftime('%Y/%b/%d'):
    print("Last date is today's date. Proceeding to weather forecast section...")
else:
    # Variables to define the start point
    start_year = 2024  # Default year
    start_month = 11   # Default month

    # If last_date exists, update start_year and start_month accordingly
    if last_date:
        last_date_obj = parse_date(last_date)
        start_year = last_date_obj.year
        start_month = last_date_obj.month + 1 if is_last_day_of_month(last_date_obj) else last_date_obj.month
        if start_month > 12:
            start_month = 1
            start_year += 1

    # Open the CSV file in append mode
    with open('weather_data_ath_pred.csv', 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        # If the CSV file is empty, add the header
        if csvfile.tell() == 0:
            csvwriter.writerow(['Date', 'Max', 'Avg', 'Min'])  # Header

        # Iterate over the years from start_year to the current year
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

                try:
                    max_retries = 3
                    retry_count = 0

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

                    if retry_count == max_retries:
                        print("Maximum retries reached. Failed to click the button.")

                    tables = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
                    )

                    main_table = tables[1]
                    sub_tables = main_table.find_elements(By.CSS_SELECTOR, 'table[aria-labelledby="Days data"]')

                    sub_table_data = []
                    for sub_table in sub_tables:
                        sub_table_rows = sub_table.find_elements(By.TAG_NAME, 'tr')
                        sub_table_data.append([[column.text.strip() for column in row.find_elements(By.TAG_NAME, 'td')]
                                               for row in sub_table_rows])

                    transposed_sub_tables = []
                    for i in range(len(sub_table_data[0])):
                        column = []
                        for sub_table in sub_table_data:
                            if i < len(sub_table):
                                column.extend(sub_table[i])
                        transposed_sub_tables.append(column)

                    for idx, row in enumerate(transposed_sub_tables):
                        if idx == 0:
                            current_month = row[0]
                            continue
                        day = int(row[0])
                        date_str = f'{year}/{current_month}/{day:02}'
                        row[0] = date_str
                        print(f"Processing date: {date_str}")

                        if any(row) and date_str not in existing_dates and date_str <= today.strftime('%Y/%b/%d'):
                            csvwriter.writerow(row[:4])
                            existing_dates.add(date_str)
                            print(f"Written to CSV: {row[:4]}")

                        # Check if we've reached today's date
                        if date_str == today.strftime('%Y/%b/%d'):
                            print("Reached today's date in historical data. Switching to forecast section...")
                            driver.quit()
                            goto_forecast_section = True
                            break
                    else:
                        continue
                    break

                finally:
                    driver.quit()


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
                max_retries = 3
                retry_count = 0
                
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
                    print("No cookie consent pop-up iframe found or handled:", e)
                
                # Retry logic with improved error handling for wuSettings button click
                retry_count = 0
                max_retries = 3

                while retry_count < max_retries:
                    try:
                        # Locate and click the wuSettings button
                        button = WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[id="wuSettings"]'))
                        )
                        driver.execute_script("arguments[0].scrollIntoView();", button)  # Ensure button is in view
                        button.click()

                        # Attempt to locate the link element after clicking wuSettings
                        link_element = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/app-tenday/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[1]/div[2]/lib-settings'))
                        )
                        link_element.click()
                        break  # Exit the loop if successful

                    except StaleElementReferenceException:
                        # Refresh the reference by retrying
                        print("Encountered StaleElementReferenceException, retrying...")
                        retry_count += 1
                        time.sleep(1)
                        
                    except TimeoutException:
                        # If element still not clickable, retry
                        retry_count += 1
                        print(f"Retry attempt {retry_count} due to TimeoutException...")
                        time.sleep(2)

                    except NoSuchElementException:
                        print("The element was not found in the DOM.")
                        break

                if retry_count == max_retries:
                    print("Maximum retries reached. Failed to click the wuSettings button or link element.")


    # Forecast section for the next day
    if last_date == today.strftime('%Y/%b/%d'):
        # Calculate tomorrow's date
        tomorrow = today + timedelta(days=1)
        tomorrow_str = tomorrow.strftime('%a %m/%d')  # Format to match displayed date on the website
        formatted_tomorrow_date = tomorrow.strftime('%Y/%b/%d')  # Format for the CSV

        # Open the forecast page
        forecast_url = "https://www.wunderground.com/forecast/gr/athens"
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(forecast_url)
        max_retries = 3
        retry_count = 0
        #try:

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
        
        while retry_count < max_retries:

                        try:
                            
                            button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[id="wuSettings"]'))
                            )
                            button.click()
                            link_element = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, '//*[@id="wuSettings-quick"]/div/a[2]'))
                            )
                            link_element.click()
                            break
                        except TimeoutException:
                            retry_count += 1
                            print(f"Retry attempt {retry_count}...")
                            time.sleep(2)


# Define a delay function to wait until a specific element confirms that the page is fully loaded
def wait_for_page_load(driver, timeout=20):
    try:
        # Wait for an element that signifies the page has fully loaded (e.g., the forecast table header or any key element)
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'obs-date')]"))
        )
    except TimeoutException:
        print("Timeout waiting for page to load.")

# Call the delay function to ensure the page loads fully
wait_for_page_load(driver)

# Calculate tomorrow's date in the format displayed on the site
today = datetime.now()
tomorrow_str = (today + timedelta(days=1)).strftime('%a %m/%d')
formatted_date = (today + timedelta(days=1)).strftime('%Y/%b/%d')

try:
    # Locate the forecast data element using the full XPath provided
    forecast_data_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((
            By.XPATH, "/html/body/app-root/app-tenday/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[2]/section/div[3]/div[1]/div/div[1]/div/lib-forecast-chart/div/div/div/lib-forecast-chart-header-daily/div/div"
        ))
    )

    # Retrieve the text content and split it into lines
    forecast_text = forecast_data_element.text.splitlines()
    
    # Define lists to hold forecast information
    dates, temps, conditions, precipitation = [], [], [], []
    
    # Patterns to classify forecast data
    date_pattern = r"[A-Za-z]{3} \d{1,2}/\d{1,2}"
    temp_pattern = r"-?\d+° \| -?\d+°C"
    precip_pattern = r"\d+(\.\d+)? mm"

    # Iterate through each line and classify the data into lists
    for line in forecast_text:
        if re.match(date_pattern, line):
            dates.append(line)
        elif re.match(temp_pattern, line):
            temps.append(line)
        elif re.match(precip_pattern, line):
            precipitation.append(line)
        elif line:  # Remaining lines are conditions
            conditions.append(line)

    # Display forecast data in table format
    print("Dates:        ", ", ".join(dates))
    print("Temperatures: ", ", ".join(temps))
    print("Conditions:   ", ", ".join(conditions))
    print("Precipitation:", ", ".join(precipitation))

    # Check if tomorrow's date is in the forecast dates
    if tomorrow_str in dates:
        # Find the index of tomorrow's date
        date_index = dates.index(tomorrow_str)
        
        # Extract temperature values and calculate the average
        min_temp, max_temp = map(int, re.findall(r"-?\d+", temps[date_index]))
        avg_temp = (min_temp + max_temp) // 2
        
        # Output in the requested format
        print(f"Forecast for {formatted_date}: {min_temp},{avg_temp},{max_temp}")
    else:
        print(f"{tomorrow_str} not found in the forecast data.")
        
        # Fallback to the first available date if tomorrow's forecast is not found
        if dates:
            min_temp, max_temp = map(int, re.findall(r"-?\d+", temps[0]))
            avg_temp = (min_temp + max_temp) // 2
            print(f"Next available forecast: {formatted_date},{min_temp},{avg_temp},{max_temp}")

except TimeoutException:
    print(f"TimeoutException: Could not locate the forecast data for {tomorrow_str}.")
except NoSuchElementException:
    print(f"NoSuchElementException: Forecast data element not found.")
except StaleElementReferenceException:
    print("Encountered StaleElementReferenceException, retrying...")

finally:
    # Close the driver
    driver.quit()