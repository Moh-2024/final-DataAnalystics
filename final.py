import pandas as pd
import re

excelFile = pd.ExcelFile(r"SeedUnofficialAppleData.xlsx")
sheetNames = excelFile.sheet_names

data = pd.read_excel(r"SeedUnofficialAppleData.xlsx", sheet_name='Sheet1')

df_cleaned = data.dropna(subset=[data.columns[0], data.columns[1]]).reset_index(drop=True)

# Renaming columns based on the first row of meaningful headers
df_cleaned.columns = ['Model', 'OS Version', 'Release Date', 'Discontinued Date', 
                      'Support End Date', 'Final OS Version', 'Lifespan', 
                      'Support Min', 'Launch Price']

# Resetting the index for a clean DataFrame
df_cleaned.reset_index(drop=True, inplace=True)


df_cleaned = df_cleaned.dropna(subset=['Model'])


# Re-applying the steps to ensure correct conversion from lifespan and support min to months, without creating additional columns
def convert_to_months(lifespan_str):
    # Extract years and months using regex
    years_match = re.search(r'(\d+)\s*year', lifespan_str)
    months_match = re.search(r'(\d+)\s*month', lifespan_str)

    years = int(years_match.group(1)) if years_match else 0
    months = int(months_match.group(1)) if months_match else 0
    
    # Convert lifespan to total months
    return years * 12 + months

# Re-applying the conversion process
df_cleaned['Lifespan'] = df_cleaned['Lifespan'].apply(lambda x: convert_to_months(x) if isinstance(x, str) else None)
df_cleaned['Support Min'] = df_cleaned['Support Min'].apply(lambda x: convert_to_months(x) if isinstance(x, str) else None)

# Removing decimal points and appending ' months' to the values
df_cleaned['Lifespan'] = df_cleaned['Lifespan'].fillna(0).astype(int).astype(str) + ' months'
df_cleaned['Support Min'] = df_cleaned['Support Min'].fillna(0).astype(int).astype(str) + ' months'

# Displaying the cleaned dataframe
df_cleaned[['Model', 'Lifespan', 'Support Min']].head()
df_cleaned = df_cleaned.drop(index=0).reset_index(drop=True)


csv_file_path = 'Cleaned_Apple_Data.csv'
df_cleaned.to_csv(csv_file_path, index=False)

# Providing the path to the user
csv_file_path

print(df_cleaned)