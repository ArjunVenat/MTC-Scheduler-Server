##Takes in Excel data, parses it into the standard format, and passes it to the solution.py file

import pandas as pd
import numpy as np

class Excel_Parser:
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.large_num = 10000 #If the time slot is unavailable, the weight x_{ijk} will be this large number
        
    def get_all_data(self):
        self.__parse_day_breakdown()
        self.__get_workers_table()
        self.__change_name_to_worker_id()
        self.__update_workers_table()        
        self.__get_preference_matrix()
        return (self.workers_table, self.preference_matrix)
        
    def __get_num_workers(self):
        self.list_of_names = pd.read_excel(self.file_path, sheet_name="List of Names")
        self.list_of_names = self.list_of_names.iloc[1:, :] #removing heading
        return len(self.list_of_names)

    def __get_workers_table(self):
        toReturn = self.list_of_names.to_numpy()
        toReturn[:, 0] = np.array([int(toReturn[x, 0] - 1) for x in range(len(toReturn))])
        self.workers_table = toReturn
        
        return self.workers_table
    
    def __parse_day_breakdown(self):
        #Some things here are hardcoded but these are for proof of concept rather than making it dynamic
        #More dynamic parsing is more suited for Qualtrics data than Excel
         
        start = 2 #Table starts at column B --> 2
        end = 11 #Table ends at column K --> 11
        self.num_workers = self.__get_num_workers()
        
        #Parse the Day Breakdown sheet
        df = pd.read_excel(self.file_path, sheet_name="Day Breakdown")
        df = df.iloc[:, start-1: end] #1 based indexing means start-1, end is just end because splicing is and [inclusive, exclusive) interval
        
        #Get all the indices of all the empty rows and filter those out
        empty_rows = df.index[df.isnull().all(axis=1)].tolist()
        df_list = np.split(df, empty_rows)
        
        #Remove additional rows with all NaN values
        for i in df_list:
            i.dropna(how='all', inplace=True)
            
        #Remove empty DataFrames from the list
        df_list = [d for d in df_list if not(d.empty)]
        
        #Set parameters i
        self.num_shifts = len((df.iloc[:, 2:]).columns) #num shifts = number of columns save for the first 2
        self.num_days = len(df_list) #num days = length of df_list, as there are 5 preference tables for each day in the spreadsheet
        self.day_breakdown_list = df_list

        for i in range(len(self.day_breakdown_list)):
            self.day_breakdown_list[i] = self.day_breakdown_list[i].iloc[2:, :]

        return self.day_breakdown_list
        
    def __change_name_to_worker_id(self):
        id_name_dict = dict(zip(self.workers_table[:, 1], self.workers_table[:, 0]))
        
        for i in self.day_breakdown_list:
            i.iloc[:, 0] = i.iloc[:, 0].replace(id_name_dict)
        

    def __update_workers_table(self):
        for day in self.day_breakdown_list:
            array_df = pd.DataFrame(self.workers_table)
            day = day.iloc[:, :2]
            day = day.rename(columns={'Unnamed: 1': 0, 'Unnamed: 2': 2})
            result = pd.merge(array_df, day.iloc[:, :2], on=0, how='left')
            self.workers_table = result.to_numpy()

        common_strings = np.array([next(x for x in row[2:] if not pd.isna(x)) for row in self.workers_table])
        self.workers_table = self.workers_table[:, :2]
        self.workers_table = np.column_stack((self.workers_table, common_strings))
        return self.workers_table
    
    def __get_preference_matrix(self):
        self.preference_matrix = np.full((self.num_workers, self.num_days, self.num_shifts), self.large_num)
        
        for j in range(self.num_days):
            for index in range(len(self.day_breakdown_list[j].iloc[:, 0])):
                for k in range(self.num_shifts):
                    i = self.day_breakdown_list[j].iloc[index, 0]
                    preference_ijk = self.day_breakdown_list[j].iloc[index, 2+k]
                    preference_ijk = self.large_num if (pd.isna(preference_ijk) or str(preference_ijk).isspace()) else int(preference_ijk)
                    self.preference_matrix[i, j, k] = preference_ijk
        
        return self.preference_matrix
    
if __name__=="__main__":
    ep = Excel_Parser("MTC Availability Template.xlsx")
    student_workers, x_ijk = ep.get_all_data()
    print(student_workers)
    print(x_ijk)
    
