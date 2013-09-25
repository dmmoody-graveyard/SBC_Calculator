import csv

def parse(raw_file, delimiter):
    """Parses a raw CSV file to a JSON-Line object."""

    # Open CSV file
    opened_file = open(raw_file)

    # Read CSV file
    csv_data = csv.reader(opened_file, delimiter=delimiter)

    # Setup an empty list
    parsed_data = []

    # Skip over the first line of the file for the headers
    fields = csv_data.next()

    # Iterate over each row of the csv file, zip together field -> value
    for row in csv_data:
        parsed_data.append(dict(zip(fields, row)))

    # Close CSV file
    opened_file.close()

    return parsed_data