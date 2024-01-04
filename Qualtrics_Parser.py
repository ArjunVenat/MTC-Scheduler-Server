!pip install xlsxwriter
import pandas as pd

def clean_and_convert(input_path, output_path):
    # Initial Qualtrics Cleaning
    df = pd.read_excel(input_path, header=1)

    original_to_new_mapping = {
        "Name": "Name",
        "Select your Position": "Position",
        "If you plan to work 2+ hours per week, would you prefer back-to-back shifts, or at different times throughout the week?": "Back-to-Back",
        "PLA's work a minimum of 1 MTC hour a week and TA's work 2. If you would prefer to work a greater number of hours than your position minimum, please indicate how many. Note that these requests cannot always be accommodated.": "Max-hours",
        "Which of the following courses do you feel qualified to Tutor?": "Courses",
    }

    time_columns = [
        "10-11 AM", "11-12 PM", "12-1 PM", "1-2 PM", "2-3 PM",
        "3-4 PM", "4-5 PM", "5-6 PM"
    ]

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    for day in days_of_week:
        for time in time_columns:
            original_column_name = f"Please indicate your availability to work at the MTC. Leave an X anytime you are unavailable, and any numbers 1-3 when you are available, where a 1 is a top preference, and a 3 is a lowest preference. Note the MTC closes at 2PM on Fridays, so leave the prefilled zeroes. - {time} - {day}"
            new_column_name = f"{time} {day}"
            original_to_new_mapping[original_column_name] = new_column_name

    df.rename(columns=original_to_new_mapping, inplace=True)

    missing_columns = [col for col in original_to_new_mapping.values() if col not in df.columns]

    if missing_columns:
        print(f"Missing columns after renaming: {missing_columns}")

    df = df[list(original_to_new_mapping.values())]

    # Save the cleaned data to a new Excel file
    df.to_excel(output_path, index=False)

    print("Cleaning complete. Saved to", output_path)

    # Adding overnight column
    df = pd.read_excel(output_path)

    day_columns = [
        ('5-6 PM Monday', '10-11 AM Tuesday'),
        ('5-6 PM Tuesday', '10-11 AM Wednesday'),
        ('5-6 PM Wednesday', '10-11 AM Thursday'),
        ('5-6 PM Thursday', '10-11 AM Friday')
    ]

    for last_shift, next_day_first_shift in day_columns:
        overnight_column_name = f'Overnight {last_shift} - {next_day_first_shift}'
        last_shift_index = df.columns.get_loc(last_shift)
        next_day_first_shift_index = df.columns.get_loc(next_day_first_shift)
        insert_index = next_day_first_shift_index
        df.insert(insert_index, overnight_column_name, 0)

    df.to_excel(output_path, index=False)

    print("Overnight columns added. Saved to", output_path)

    # Convert to preference values
    df = pd.read_excel(output_path)

    all_time_columns = [
        '10-11 AM Monday', '11-12 PM Monday', '12-1 PM Monday', '1-2 PM Monday', '2-3 PM Monday',
        '3-4 PM Monday', '4-5 PM Monday', '5-6 PM Monday',
        'Overnight 5-6 PM Monday - 10-11 AM Tuesday',
        '10-11 AM Tuesday', '11-12 PM Tuesday', '12-1 PM Tuesday', '1-2 PM Tuesday', '2-3 PM Tuesday',
        '3-4 PM Tuesday', '4-5 PM Tuesday', '5-6 PM Tuesday',
        'Overnight 5-6 PM Tuesday - 10-11 AM Wednesday',
        '10-11 AM Wednesday', '11-12 PM Wednesday', '12-1 PM Wednesday', '1-2 PM Wednesday', '2-3 PM Wednesday',
        '3-4 PM Wednesday', '4-5 PM Wednesday', '5-6 PM Wednesday',
        'Overnight 5-6 PM Wednesday - 10-11 AM Thursday',
        '10-11 AM Thursday', '11-12 PM Thursday', '12-1 PM Thursday', '1-2 PM Thursday', '2-3 PM Thursday',
        '3-4 PM Thursday', '4-5 PM Thursday', '5-6 PM Thursday',
        'Overnight 5-6 PM Thursday - 10-11 AM Friday',
        '10-11 AM Friday', '11-12 PM Friday', '12-1 PM Friday', '1-2 PM Friday', '2-3 PM Friday',
        '3-4 PM Friday', '4-5 PM Friday', '5-6 PM Friday'
    ]

    for column in all_time_columns:
        df[column] = df[column].apply(lambda x: 10000 if (x == "X" or x == 0) else x ** 2)

    df.to_excel(output_path, index=False)

    print("Conversion to preference values complete. Saved to", output_path)

# Example usage
input_path = "/content/MTC Availability_December 25, 2023_18.37.xlsx"
output_path = "final_cleaned_and_converted.xlsx"
clean_and_convert(input_path, output_path)
