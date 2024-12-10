
# !!! WORKING and identifies also if it is the last day of the month and insert remaining days.

import csv, os, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import date, datetime
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException


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

# Check if the CSV file exists and is not empty
if os.path.isfile('weather_data_ath.csv') and os.path.getsize('weather_data_ath.csv') > 0:
    with open('weather_data_ath.csv', 'r') as csvfile:
        last_date = None
        print("last date is =", last_date)
        for line in csvfile.readlines():
            if line.strip():
                last_date = line.split(',')[0]  # Assuming date is the first column
                print("Last Date =", last_date)

# Initialize start_year with a default value
start_year = 2023
# start_month = Jan
# start_day = 1
last_date = None

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
    start_month = 1

# Open the CSV file in append mode
with open('weather_data_ath.csv', 'a', newline='') as csvfile:
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