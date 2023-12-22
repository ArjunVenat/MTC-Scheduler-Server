##Takes in Excel data, parses it into the standard format, and passes it to the solution.py file

import pandas as pd
import numpy as np

class Excel_Parser:
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.largeNum = np.inf #If the time slot is unavailable, the weight x_{ijk} will be this large number

        
    def get_num_workers(self):
        self.list_of_names = pd.read_excel(self.file_path, sheet_name="List of Names")
        self.list_of_names = self.list_of_names.iloc[1:, :] #removing heading
        return len(self.list_of_names)

    def get_workers_table(self):
        #I envision the workers table having the id, name, and position of the worker
        #id is the index for the worker, like the indexed by i in the formulation
        #can use np.where() to filter by position to get the necessary sets
        
        toReturn = self.list_of_names.to_numpy()
        toReturn[:, 0] = np.array([int(toReturn[x, 0] - 1) for x in range(len(toReturn))])
        self.workers_table = toReturn
        
        return self.workers_table
    
    def parse_day_breakdown(self):
        #Some things here are hardcoded but these are for proof of concept rather than making it dynamic
        #More dynamic parsing is more suited for Qualtrics data than Excel
         
        start = 2 #Table starts at column B --> 2
        end = 11 #Table ends at column K --> 11
        self.num_workers = self.get_num_workers()
        
        #Parse the Day Breakdown sheet
        df = pd.read_excel(self.file_path, sheet_name="Day Breakdown")
        
        df = df.iloc[:, start-1: end] #1 based indexing means start-1, end is just end because splicing is and [inclusive, exclusive) interval
        #Get all the index of all the empty rows and filter those out
        empty_rows = df.index[df.isnull().all(axis=1)].tolist()  
        df_list = np.split(df, empty_rows)
        
        #Remove additional rows with all NaN values
        for i in df_list:
            i.dropna(how='all', inplace=True)
            
        #Remove empty DataFrames from the list
        df_list = [d for d in df_list if not(d.empty)]
        
        self.num_shifts = len((df.iloc[:, 2:]).columns) #num shifts = number of columns save for the first 2
        self.num_days = len(df_list) #num days = length of df_list, as there are 5 preference tables for each day in the spreadsheet
        self.day_breakdown_list = df_list

        
        #Printing the output
        #for df in self.day_breakdown_list:
        #    print(df, '\n')
        
        return self.day_breakdown_list
        
    def change_name_to_worker_id(self):
        #Currently working on this part
        print(self.workers_table)
        
        for i in self.day_breakdown_list:
            temp = i.iloc[2:, 0]
            for row in temp:
                id = self.workers_table[np.where(self.workers_table == row), 0]
                row = id[0]
            print(temp)
                            
    def get_preference_matrix(self):
        self.pref_matrix = np.full((self.num_workers, self.num_days, self.num_shifts), self.largeNum)
        return self.pref_matrix
        
if __name__=="__main__":
    ep = Excel_Parser("MTC Availability Template.xlsx")
    df = ep.parse_day_breakdown()
     
    
    workers_table = ep.get_workers_table()
    #preference_matrix = ep.get_preference_matrix()
    
    
    #print(ep.num_workers())
    
    #x_ijk = ep.get_preference_matrix()
    #print(x_ijk.shape)
    
    #ep.change_name_to_worker_id()
