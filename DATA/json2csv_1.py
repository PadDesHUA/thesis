import json
import csv
from datetime import datetime, timezone

def unix_time_to_date(unix_time):
    return datetime.fromtimestamp(unix_time, tz=timezone.utc).strftime('%Y-%m-%d')

def bytes_to_gb(bytes_data):
    gb = bytes_data / (1024 ** 3)
    return round(gb, 2)

# Load JSON data
with open('data.json', 'r', encoding='utf-8-sig') as json_file:
    data = json.load(json_file)

# Convert to CSV
csv_data = []
for entry in data:
    date = unix_time_to_date(entry[0])
    data_in_gb = bytes_to_gb(entry[1])
    data_in_avg_gb = bytes_to_gb(entry[2])
    data_out_gb = bytes_to_gb(entry[3])
    data_out_avg_gb = bytes_to_gb(entry[4])
    csv_data.append([date, data_in_gb, data_in_avg_gb, data_out_gb, data_out_avg_gb])

# Write CSV
with open('internet_usage_converted.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Date', 'DataIn(GB)', 'DataInAvg(GB)', 'DataOut(GB)', 'DataOutAvg(GB)'])
    writer.writerows(csv_data)

print("CSV file generated successfully!")

