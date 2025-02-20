import csv
import subprocess
from datetime import datetime, timezone
import os

# Execute curl command to get JSON data
curl_command = "curl -X GET 'https://portal.gr-ix.gr/grapher/ixp?period=year&type=log&category=bits&protocol=all&id=1'"
output = subprocess.check_output(curl_command, shell=True).decode('utf-8')

# Parse JSON data
data = eval(output)

# Convert Unix timestamps to human-readable dates
current_date = datetime.now().strftime('%Y/%m/%d')
last_entry_date = None
updated_data = []

# Check if the file exists
file_exists = os.path.exists('output_data.csv')

# If the file exists and is not empty, read the data and check the last date
if file_exists and os.path.getsize('output_data.csv') > 0:
    with open('output_data.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Read the header
        updated_data = list(reader)  # Existing data
    
    # Get the last date in the existing data
    last_entry_date = updated_data[-1][0] if updated_data else None

# Convert the fetched data to human-readable format and check for missing dates
new_data = []
for item in data:
    timestamp = item[0]
    date = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y/%m/%d')  # Convert timestamp to date
    input_during_interval_tb = item[1] / 10**12  # Convert GB to TB
    input_average_tb = item[2] / 10**12  # Convert GB to TB
    output_during_interval_tb = item[3] / 10**12  # Convert GB to TB
    output_average_tb = item[4] / 10**12  # Convert GB to TB
    converted_item = [date, input_during_interval_tb, input_average_tb, output_during_interval_tb, output_average_tb]

    # If there's no last date or the date is missing, add the new entry
    if last_entry_date is None or date > last_entry_date:
        new_data.append(converted_item)

# Append the new data at the end if any data is missing
if new_data:
    with open('output_data.csv', 'a', newline='') as csvfile:  # Open in append mode
        writer = csv.writer(csvfile)

        # If file is empty, write the header first
        if not file_exists or os.path.getsize('output_data.csv') == 0:
            writer.writerow(['Date', 'DataIn(TB)', 'DataInAvg(TB)', 'DataOut(TB)', 'DataOutAvg(TB)'])

        # Write the new rows at the end of the file
        writer.writerows(new_data)

print("Data has been written to output_data.csv")


# # ### WORKING for adding only one day at the end

# # import csv
# # import subprocess
# # from datetime import datetime, timezone
# # import os

# # # Execute curl command to get JSON data
# # curl_command = "curl -X GET 'https://portal.gr-ix.gr/grapher/ixp?period=year&type=log&category=bits&protocol=all&id=1'"
# # output = subprocess.check_output(curl_command, shell=True).decode('utf-8')

# # # Parse JSON data
# # data = eval(output)

# # # Convert Unix timestamps to human-readable dates
# # current_date = datetime.now().strftime('%Y/%m/%d')
# # last_entry_date = None
# # updated_data = []

# # # Check if the file exists
# # file_exists = os.path.exists('output_data.csv')

# # # If the file exists and is not empty, read the data and check the last date
# # if file_exists and os.path.getsize('output_data.csv') > 0:
# #     with open('output_data.csv', 'r') as csvfile:
# #         reader = csv.reader(csvfile)
# #         header = next(reader)  # Read the header
# #         updated_data = list(reader)  # Existing data
    
# #     # Get the last date in the existing data
# #     last_entry_date = updated_data[-1][0] if updated_data else None

# # # Convert the fetched data to human-readable format and check for missing dates
# # new_data = []
# # for item in data:
# #     timestamp = item[0]
# #     date = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y/%m/%d')  # Convert timestamp to date
# #     input_during_interval_tb = item[1] / 10**6  # Convert GB to TB
# #     input_average_tb = item[2] / 10**6  # Convert GB to TB
# #     output_during_interval_tb = item[3] / 10**6  # Convert GB to TB
# #     output_average_tb = item[4] / 10**6  # Convert GB to TB
# #     converted_item = [date, input_during_interval_tb, input_average_tb, output_during_interval_tb, output_average_tb]

# #     # If there's no last date or the date is missing, add the new entry
# #     if last_entry_date is None or date > last_entry_date:
# #         new_data.append(converted_item)

# # # Append the new data at the end if any data is missing
# # if new_data:
# #     with open('output_data.csv', 'a', newline='') as csvfile:  # Open in append mode
# #         writer = csv.writer(csvfile)

# #         # If file is empty, write the header first
# #         if not file_exists or os.path.getsize('output_data.csv') == 0:
# #             writer.writerow(['Date', 'DataIn(TB)', 'DataInAvg(TB)', 'DataOut(TB)', 'DataOutAvg(TB)'])

# #         # Write the new rows at the end of the file
# #         writer.writerows(new_data)

# # print("Data has been written to output_data.csv")




### Working with TB format and date format correct

# import csv
# import subprocess
# from datetime import datetime, timezone

# # Execute curl command to get JSON data
# curl_command = "curl -X GET 'https://portal.gr-ix.gr/grapher/ixp?period=year&type=log&category=bits&protocol=all&id=1'"
# output = subprocess.check_output(curl_command, shell=True).decode('utf-8')

# # Parse JSON data
# data = eval(output)

# # Convert Unix timestamps to human-readable dates
# converted_data = []
# for item in data:
#     timestamp = item[0]
#     date = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y/%m/%d')  # Change date format
#     input_during_interval_gb = item[1] / 10**12
#     input_average_gb = item[2] / 10**12
#     output_during_interval_gb = item[3] / 10**12
#     output_average_gb = item[4] / 10**12
#     converted_item = [date, input_during_interval_gb, input_average_gb, output_during_interval_gb, output_average_gb]
#     converted_data.append(converted_item)

# # Write data to CSV file
# with open('output_data.csv', 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow(['Date', 'DataIn(GB)', 'DataInAvg(GB)', 'DataOut(GB)', 'DataOutAvg(GB)'])  # Update header
#     writer.writerows(converted_data)

# print("Data has been written to output_data.csv")


# import csv
# import subprocess
# from datetime import datetime, timezone

# # Execute curl command to get JSON data
# curl_command = "curl -X GET 'https://portal.gr-ix.gr/grapher/ixp?period=year&type=log&category=bits&protocol=all&id=1'"
# output = subprocess.check_output(curl_command, shell=True).decode('utf-8')

# # Parse JSON data
# data = eval(output)

# # Convert Unix timestamps to human-readable dates
# converted_data = []
# for item in data:
#     timestamp = item[0]
#     date = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d')
#     input_during_interval_gb = item[1] / 10**9
#     input_average_gb = item[2] / 10**9
#     output_during_interval_gb = item[3] / 10**9
#     output_average_gb = item[4] / 10**9
#     converted_item = [date, input_during_interval_gb, input_average_gb, output_during_interval_gb, output_average_gb]
#     #converted_item = [date] + item[1:]
#     converted_data.append(converted_item)

# # Write data to CSV file
# with open('output_data.csv', 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow(['Date', 'Unix Time', 'Input During Interval (GB)', 'Input Average (GB)', 'Output During Interval (GB)', 'Output Average (GB)'])
#     #writer.writerow(['Date', 'Unix Time', 'Input During Interval (Bytes)', 'Input Average (Bytes)', 'Output During Interval (Bytes)', 'Output Average (Bytes)'])
#     writer.writerows(converted_data)

# print("Data has been written to output_data.csv")
