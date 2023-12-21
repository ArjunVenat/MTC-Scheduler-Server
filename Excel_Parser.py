import pandas as pd
import numpy as np

class Excel_Parser:
    def __init__(self, file_path):
        self.file_path = file_path
        
    def get_num_workers(self):
        df = pd.read_excel(self.file_path, sheet_name="List of Names")
        df = df.iloc[1:, :] #removing heading
        return len(df)

    def parse_day_breakdown(self):
        #Some are hardcoded but these are for proof of concept rather than making it dynamic
        #More dynamic parsing is more suited for Qualtrics data than Excel
         
        start = 2
        end = 11
        self.num_shifts = 8
        self.num_days = 5
        self.num_workers = self.get_num_workers()
        
        df = pd.read_excel(self.file_path, sheet_name="Day Breakdown")
        df = df.iloc[:, start-1: end]
        return df
        
    def get_preference_matrix(self):
        np.zeros()
        
if __name__=="__main__":
    ep = Excel_Parser("MTC Availability Template.xlsx")
    df = ep.parse_day_breakdown()
    print(ep.num_workers())
    print(df)
