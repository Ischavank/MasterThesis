#step2: creates decimals if needed
import csv

input_file = 'data_raw2.csv'
output_file = 'data_raw3.csv'

def format_number(value):
    try:
        num = float(value)
        # Check how many decimals there are
        decimals = value.strip().split(".")[1] if "." in value else ""
        if len(decimals) > 3:
            return f"{num:.3f}"
        else:
            return value
    except ValueError:
        return value  # Return non-numeric values unchanged

with open(input_file, mode='r', newline='') as infile, \
     open(output_file, mode='w', newline='') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        new_row = [format_number(cell) for cell in row]
        writer.writerow(new_row)

print(f"All numeric values rounded to max 3 decimals in '{output_file}'")
