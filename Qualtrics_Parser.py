import pandas as pd
import numpy as np

def clean_data(
    # DYNAMIC - update time_columns to read in from front end
    input_path, 
    social_credit_score_list,
    priority_list,
    time_columns=[
        "10-11 AM", "11-12 PM", "12-1 PM", "1-2 PM", "2-3 PM",
        "3-4 PM", "4-5 PM", "5-6 PM"],
    days_of_week=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    ):

    # Initial Qualtrics Cleaning
    df = pd.read_excel(input_path, header=1)

    # DYNAMIC - Update mapping to read in from front end - some is required, other is arbitrary as the survey changes with time, so needs to be dynamic
    original_to_new_mapping = {
        "Name": "Name",
        "Select your Position": "Position",
        "PLA's and Graders work a minimum of 1 hour a week in the MTC, while TA's and GLA's work 2 hours per week in the MTC. If you'd like to work additional hours, please indicate the maximum number of hours you would like to work in a week, otherwise leave this field blank.": "Max-hours",
        "If you plan to work more than one shift, would you prefer back-to-back shifts, or at different times throughout the week?": "Back-to-Back",
        "Which of the following courses do you feel qualified to Tutor?": "Courses",
    }

    # DYNAMIC - Update time_columns - read in from front end
    for day in days_of_week:
        for time in time_columns:
            original_column_name = f"Please indicate your availability to work at the MTC. Leave an X anytime you are unavailable, and any numbers 1-3 when you are available, where a 1 is a top preference, and a 3 is a lowest preference. Note the MTC closes at 2PM on Fridays, so leave the prefilled X's. Answer as many choices as you can, or we may follow up and ask you to resubmit. - {time} - {day}"
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
        elif row["Position"] in ["PLA", "Grader/ Tutor"]:
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
    # Insert social_credit_score column into df
    df.insert(loc=6, column="social_credit_score", value=social_credit_score_list)
    df.insert(loc=7, column="prioritized?", value=["Yes" if x else "No" for x in priority_list])

    return df

# DYNAMIC - Note that time_columns will now be read in as a specification from the front end
def parse_data(
    df,
    social_credit_score_list,
    priority_list,
    time_columns=[
        "10-11 AM", "11-12 PM", "12-1 PM", "1-2 PM", "2-3 PM",
        "3-4 PM", "4-5 PM", "5-6 PM"],
    days_of_week=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    ):

    #Correct the index column and update the new scores
    df.iloc[:, 0] = range(len(df)) 
    df.iloc[:, 6] = social_credit_score_list 
    df.iloc[:, 7] = ["Yes" if x else "No" for x in priority_list]

    # DYNAMIC - this will depend on if any additional columns are in the cleaned data
    starting_of_preferences = 8 #number of first few columns


    student_workers = df.iloc[:, :starting_of_preferences].to_numpy()
    preferences = df.iloc[:, starting_of_preferences:]

    x_ijk = np.zeros((len(df), len(days_of_week), len(time_columns)))

    for i in range(len(df)):
        for j in range(len(days_of_week)):
            for k in range(len(time_columns)):
                x_ijk[i, j, k] = int(preferences.iloc[i, len(time_columns) * j + k])
                if (priority_list[i] == "Yes" or priority_list[i] == True):
                    if x_ijk[i, j, k] == 1:
                        x_ijk[i, j, k] = 0.5
                    elif x_ijk[i, j, k] == 4:
                        x_ijk[i, j, k] = 2
                    elif x_ijk[i, j, k] == 9:
                        x_ijk[i, j, k] = 18
                    elif x_ijk[i, j, k] == 10000:
                        x_ijk[i, j, k] = 20000

    # Read preference scores into data frame and cut it in half for workers who are prioritized
    print(x_ijk.shape)

    return (student_workers, x_ijk)

if __name__ == "__main__":
    # Example usage
    input_path = "MTC - D24 Availability_February 20, 2024_21.31.xlsx"
    cleaned_input_path = "final_cleaned_and_converted.xlsx"

    #If you want to make changes to the "final_cleaned_and_converted.xlsx" file, then keep the 4 lines below as is, otherwise comment out 

    social_credit_score_list = [2] * 49 #change this as you wish but we have 49 MTC workers and by default I have them getting all 3's
    priority_list = [True] * 49
    cleaned_df = clean_data(input_path, social_credit_score_list, priority_list)
    cleaned_df.to_excel(cleaned_input_path, index=False)

    cleaned_df = pd.read_excel(cleaned_input_path)
    student_workers, x_ijk = parse_data(cleaned_df)
