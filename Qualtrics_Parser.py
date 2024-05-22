import pandas as pd
import numpy as np
import re

def clean_data(
    # DYNAMIC - update time_columns to read in from front end
    input_path, 
    social_credit_score_list,
    priority_list,
    original_to_new_mapping,
    # included_list
    ):
    print("this")
    # Initial Qualtrics Cleaning
    df = pd.read_excel(input_path, header=1)

    # DYNAMIC - Update mapping to read in from front end - some is required, other is arbitrary as the survey changes with time, so needs to be dynamic
    #original_to_new_mapping = {
        #"Name": "Name",
        #"Select your Position": "Position",
        #"PLA's and Graders work a minimum of 1 hour a week in the MTC, while TA's and GLA's work 2 hours per week in the MTC. If you'd like to work additional hours, please indicate the maximum number of hours you would like to work in a week, otherwise leave this field blank.": "Max-hours",
        #"If you plan to work more than one shift, would you prefer back-to-back shifts, or at different times throughout the week?": "Back-to-Back",
        #"Which of the following courses do you feel qualified to Tutor?": "Courses",
    #}
    
    # for newMapping in original_to_new_mapping:
    #     colToMap = [col for col in df.columns if (newMapping.lower() in str(col).lower())]
    #     for column in colToMap:
    #         newName = original_to_new_mapping[newMapping]
    #         df.rename(columns={column: newName}, inplace=True)
    #     df.rename(columns=original_to_new_mapping, inplace=True)

    # print(df.columns)
    pattern = r'^(.+) - (\d{1,2}-\d{1,2} [AP]M) - ([A-Za-z]+)$'
    matching_columns = []
    for col in df.columns:
        match = re.match(pattern, col)
        if match:
            print(match)
            renamed_col = match.group(2) + " " + match.group(3)
            matching_columns.append((col, renamed_col))
    
    for old_col, new_col in matching_columns:
        df.rename(columns={old_col: new_col}, inplace=True)
        df[new_col] = df[new_col].apply(lambda x: x**2 if (x > 0) else 10000)

    print(df.columns)
    print(original_to_new_mapping)
    df.rename(columns=original_to_new_mapping, inplace=True)
    columns_to_drop = ['Start Date', 'End Date', 'Response Type', 'IP Address',
                     'Progress', 'Duration (in seconds)', 'Finished', 'Recorded Date',
                     'Response ID', 'Recipient Last Name', 'Recipient First Name',
                     'Recipient Email', 'External Data Reference', 'Location Latitude',
                     'Location Longitude', 'Distribution Channel', 'User Language', "Exclude"]
    
    df = df.drop(columns=columns_to_drop)
    print(df.columns)
    print("See here ^")

    missing_columns = [col for col in original_to_new_mapping.values() if col not in df.columns]

    if missing_columns:
        print(f"Missing columns after renaming: {missing_columns}")

    #df = df[list(original_to_new_mapping.values())]


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
    coursesIndex = df.columns.get_loc('Courses')
    df.insert(loc=coursesIndex+1, column="social_credit_score", value=social_credit_score_list)
    df.insert(loc=coursesIndex+2, column="prioritized?", value=["No" for x in priority_list])

    firstFewCols = ["Index", "Name", "Position", "Max-hours", "Back-to-Back", "Courses", "social_credit_score", "prioritized?"]
    remainingCols = [col for col in df.columns if col not in firstFewCols]
    newOrder = firstFewCols + remainingCols
    df = df[newOrder]

    #Order the time columns
    

    # Filter out columns based on "included_list"
    # included_columns = filter(lambda col: included_list[col], range(len(df.columns)))
    # df = df.iloc[:, included_columns]

    return df

# DYNAMIC - Note that time_columns will now be read in as a specification from the front end
def parse_data(
    df,
    social_credit_score_list,
    priority_list,
    time_columns,
    days_of_week
    ):

    #Correct the index column and update the new scores
    df.iloc[:, 0] = range(len(df))
    df["social_credit_score"] = social_credit_score_list
    df["prioritized?"] = ["Yes" if x else "No" for x in priority_list]

    starting_of_preferences = df.columns.get_loc('prioritized?') + 3

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
    original_to_new_mapping = {
        "Name": "Name",
        "Select your Position": "Position",
        "PLA's and Graders work a minimum of 1 hour a week in the MTC, while TA's and GLA's work 2 hours per week in the MTC. If you'd like to work additional hours, please indicate the maximum number of hours you would like to work in a week, otherwise leave this field blank.": "Max-hours",
        "If you plan to work more than one shift, would you prefer back-to-back shifts, or at different times throughout the week?": "Back-to-Back",
        "Which of the following courses do you feel qualified to Tutor?": "Courses",
    }
    time_columns=[

        "10-11 AM", "11-12 PM", "12-1 PM", "1-2 PM", "2-3 PM",

        "3-4 PM", "4-5 PM", "5-6 PM"],

    days_of_week=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    cleaned_df = clean_data(input_path, 
    social_credit_score_list,
    priority_list,
    original_to_new_mapping,
    time_columns,
    days_of_week)
    cleaned_df.to_excel(cleaned_input_path, index=False)

    cleaned_df = pd.read_excel(cleaned_input_path)
    student_workers, x_ijk = parse_data(cleaned_df)
