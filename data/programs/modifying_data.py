import csv

# Config
input_file = "data_raw1.csv"
output_file = "data_raw2.csv"
target_column = "validation"
new_value = "yes"
start_line = 89
end_line = 136

with open(input_file, mode="r", newline="") as infile, open(output_file, mode="w", newline="") as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames

    if target_column not in fieldnames:
        raise ValueError(f"Column '{target_column}' not found in CSV headers.")

    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for i, row in enumerate(reader, start=2):  # start=2 since header is line 1
        if start_line+1 <= i <= end_line+1:
            row[target_column] = new_value
        writer.writerow(row)
