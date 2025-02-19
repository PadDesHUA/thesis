import csv
import subprocess
from datetime import datetime, timezone

# Execute curl command to get JSON data
curl_command = "curl -X GET 'https://portal.gr-ix.gr/grapher/ixp?period=year&type=log&category=bits&protocol=all&id=1'"
output = subprocess.check_output(curl_command, shell=True).decode('utf-8')

# Parse JSON data
data = eval(output)

# Convert Unix timestamps to human-readable dates
converted_data = []
for item in data:
    timestamp = item[0]
    date = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y/%m/%d')  # Change date format
    input_during_interval_gb = item[1] / 10**9
    input_average_gb = item[2] / 10**9
    output_during_interval_gb = item[3] / 10**9
    output_average_gb = item[4] / 10**9
    converted_item = [date, input_during_interval_gb, input_average_gb, output_during_interval_gb, output_average_gb]
    converted_data.append(converted_item)

# Write data to CSV file
with open('output_data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Date', 'DataIn(GB)', 'DataInAvg(GB)', 'DataOut(GB)', 'DataOutAvg(GB)'])  # Update header
    writer.writerows(converted_data)

print("Data has been written to output_data.csv")


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
