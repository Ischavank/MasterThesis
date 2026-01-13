import csv

input_file = "data_raw3.csv"
output_file = "data_raw4.csv"
target_column = "API_water_def"

with open(input_file, newline="") as infile, open(output_file, mode="w", newline="") as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        try:
            row[target_column] = round(float(row[target_column]) * 100,1)
        except ValueError:
            pass  # Skip if not numeric
        writer.writerow(row)
