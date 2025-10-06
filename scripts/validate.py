import json
import sys
from datetime import datetime

def validate_removals_data(filepath):
    """
    Validate the structure and content of removals.json
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("Error: Data must be a list")
            return False

        required_fields = {'destination_country', 'date', 'number_removed', 'origin_nationalities'}
        optional_fields = {'date_range_end', 'agency', 'flight_numbers', 'aircraft_types',
                          'imprisoned', 'ongoing', 'source_urls', 'notes'}

        valid = True
        for i, entry in enumerate(data):
            if not isinstance(entry, dict):
                print(f"Error: Entry {i} is not a dictionary")
                valid = False
                continue

            # Check required fields
            missing_fields = required_fields - set(entry.keys())
            if missing_fields:
                print(f"Error: Entry {i} missing required fields: {missing_fields}")
                valid = False

            # Validate date format
            if entry.get('date'):
                try:
                    datetime.strptime(entry['date'], '%Y-%m-%d')
                except ValueError:
                    print(f"Error: Entry {i} has invalid date format: {entry['date']}")
                    valid = False

            # Validate number_removed
            if entry.get('number_removed') is not None:
                if not isinstance(entry['number_removed'], (int, type(None))):
                    print(f"Error: Entry {i} number_removed must be integer or null")
                    valid = False

            # Validate origin_nationalities
            if not isinstance(entry.get('origin_nationalities', []), list):
                print(f"Error: Entry {i} origin_nationalities must be a list")
                valid = False

        if valid:
            print("Validation passed!")
        else:
            print("Validation failed!")

        return valid

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate.py <filepath>")
        sys.exit(1)

    validate_removals_data(sys.argv[1])