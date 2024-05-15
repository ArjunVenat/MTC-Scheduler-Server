import pandas as pd

def get_column_names(qualtrics_data, dataType):

  def get_column_names_raw_data(qualtrics_data_df):
      columns_to_drop = ['Start Date', 'End Date', 'Response Type', 'IP Address',
                     'Progress', 'Duration (in seconds)', 'Finished', 'Recorded Date',
                     'Response ID', 'Recipient Last Name', 'Recipient First Name',
                     'Recipient Email', 'External Data Reference', 'Location Latitude',
                     'Location Longitude', 'Distribution Channel', 'User Language']
  
      columns_to_drop.extend([col for col in qualtrics_data_df.columns if col.startswith(('Please'))])
      cleaned_data_df = qualtrics_data_df.drop(columns=columns_to_drop)
  
      return cleaned_data_df.columns
  
  def get_column_names_cleaned_data(qualtrics_data_df):
      social_credit_score_default = 3
      prioritized_default = "No"
  
      filtered_cleaned_data = qualtrics_data_df[['Name', 'Position']].assign(
          social_credit_score=social_credit_score_default,
          prioritized=prioritized_default
      )
      return filtered_cleaned_data.columns

  
  if dataType == "raw":
    columns = get_column_names_raw_data(qualtrics_data)
  else:
    columns = get_column_names_cleaned_data(qualtrics_data)

  return columns