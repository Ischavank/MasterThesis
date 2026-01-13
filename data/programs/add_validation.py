#step1, add new column based on values in other columns
#needed: already the new header

import csv

input_file = 'data_raw1.csv'
output_file = 'data_raw3.csv'

input_column = 'soil_moist'
output_column = 'soil_validation'

soil_moisture_limit = 20

with open(input_file, mode='r', newline='') as infile, \
     open(output_file, mode='w', newline='') as outfile:
    
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames

    if input_column not in fieldnames or output_column not in fieldnames:
        raise ValueError(f"Input CSV must contain {input_column} and {output_column} columns.")

    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        try:
            moisture = float(row[input_column])
            row[output_column] = 'A' if moisture < soil_moisture_limit else 'B'
        except ValueError:
            row[output_column] = ''  # or handle as needed for bad/missing data
            print(f"row {row} misses a value for soil moisture content")
        writer.writerow(row)

print(f"Updated rows written to '{output_file}'")
