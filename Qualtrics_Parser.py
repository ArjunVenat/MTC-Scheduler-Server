import pandas as pd
import numpy as np

def clean_data(
    input_path, 
    social_credit_score,
    prioritize,
    time_columns=[
        "10-11 AM", "11-12 PM", "12-1 PM", "1-2 PM", "2-3 PM",
        "3-4 PM", "4-5 PM", "5-6 PM"],
    days_of_week=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    ):

    # Initial Qualtrics Cleaning
    df = pd.read_excel(input_path, header=1)

    original_to_new_mapping = {
        "Name": "Name",
        "Select your Position": "Position",
        "PLA's and Graders work a minimum of 1 hour a week, while TA's and GLA's work 2. If you'd like to work additional hours, please indicate the maximum number of hours you would like to work in a week, otherwise leave this field blank.": "Max-hours",
        "If you plan to work more than one shift, would you prefer back-to-back shifts, or at different times throughout the week?": "Back-to-Back",
        "Which of the following courses do you feel qualified to Tutor?": "Courses",
    }

    for day in days_of_week:
        for time in time_columns:
            original_column_name = f"Please indicate your availability to work at the MTC. Leave an X anytime you are unavailable, and any numbers 1-3 when you are available, where a 1 is a top preference, and a 3 is a lowest preference. Note the MTC closes at 2PM on Fridays, so leave the prefilled X's. - {time} - {day}"
            new_column_name = f"{time} {day}"
            original_to_new_mapping[original_column_name] = new_column_name

    df.rename(columns=original_to_new_mapping, inplace=True)

    missing_columns = [col for col in original_to_new_mapping.values() if col not in df.columns]

    if missing_columns:
        print(f"Missing columns after renaming: {missing_columns}")

    df = df[list(original_to_new_mapping.values())]

    all_time_columns = [f"{i} {j}" for j in days_of_week for i in time_columns]

    for column in all_time_columns:
        df[column] = df[column].apply(lambda x: x**2 if (x > 0) else 10000)


    def update_max_hours(row):
        if pd.notna(row["Max-hours"]):
            return row["Max-hours"]
        elif row["Position"] in ["PLA", "Grader/ Greeter"]:
            return 1
        else:
            return 2

    def update_back_to_back(row):
        if row["Max-hours"] in [1]:
            return "NaN"
        else:
            return row["Back-to-Back"]

    df["Max-hours"] = df.apply(update_max_hours, axis=1)
    df["Back-to-Back"] = df.apply(update_back_to_back, axis=1)

    # Add an "Index" column starting from 0
    df.insert(0, "Index", range(len(df)))

    return df


def clean_and_parse(    
    input_path,
    social_credit_score,
    prioritize,
    time_columns=[
        "10-11 AM", "11-12 PM", "12-1 PM", "1-2 PM", "2-3 PM",
        "3-4 PM", "4-5 PM", "5-6 PM"],
    days_of_week=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    ):

    df = clean_data(input_path, social_credit_score, prioritize)

    # Insert social_credit_score column into df
    df.insert(loc=1, column="social_credit_score", value=social_credit_score)

    student_workers = df.iloc[:, :7].to_numpy()
    preferences = df.iloc[:, 7:]
    x_ijk = np.zeros((len(df), len(days_of_week), len(time_columns)))

    # Read preference scores into data frame and cut it in half for workers who are prioritized
    for i in range(len(df)):
        for j in range(len(days_of_week)):
            for k in range(len(time_columns)):
                x_ijk[i, j, k] = int(preferences.iloc[i, len(time_columns) * j + k])
                if prioritize[i] == 1 and x_ijk[i, j, k] != 10000:
                    x_ijk[i, j, k] = x_ijk[i, j, k] / 2
                elif prioritize[i] == 1 and x_ijk[i, j, k] == 10000:
                    x_ijk[i, j, k] = x_ijk[i, j, k] * 2
                    

    return df, (student_workers, x_ijk)

if __name__ == "__main__":
    # Example usage
    input_path = "MTC Availability_January 7, 2024_15.11.xlsx"
    cleaned_df, (student_workers, x_ijk) = clean_and_parse(input_path)

    cleaned_df.to_excel("final_cleaned_and_converted.xlsx", index=False)
