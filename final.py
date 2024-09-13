import pandas as pd
import re

excelFile = pd.ExcelFile(r"SeedUnofficialAppleData.xlsx")
sheetNames = excelFile.sheet_names

data = pd.read_excel(r"SeedUnofficialAppleData.xlsx", sheet_name='Sheet1')

CleanedData = data.dropna(subset=[data.columns[0], data.columns[1]]).reset_index(drop=True)

# Renaming columns
CleanedData.columns = ['Model', 'OS Version', 'Release Date', 'Discontinued Date', 
                      'Support End Date', 'Final OS Version', 'Lifespan', 
                      'Support Min', 'Launch Price']

# Resetting the index for a clean DataFrame
CleanedData.reset_index(drop=True, inplace=True)


CleanedData = CleanedData.dropna(subset=['Model'])


#Changing years to months
def convert_to_months(lifespan_str):
    # Extract years and months using regex
    years_match = re.search(r'(\d+)\s*year', lifespan_str)
    months_match = re.search(r'(\d+)\s*month', lifespan_str)

    years = int(years_match.group(1)) if years_match else 0
    months = int(months_match.group(1)) if months_match else 0
    
    # Convert lifespan to total months
    return years * 12 + months

# Re-applying the conversion process
CleanedData['Lifespan'] = CleanedData['Lifespan'].apply(lambda x: convert_to_months(x) if isinstance(x, str) else None)
CleanedData['Support Min'] = CleanedData['Support Min'].apply(lambda x: convert_to_months(x) if isinstance(x, str) else None)

# Removing decimal points and appending ' months' to the values
CleanedData['Lifespan'] = CleanedData['Lifespan'].fillna(0).astype(int).astype(str) + ' months'
CleanedData['Support Min'] = CleanedData['Support Min'].fillna(0).astype(int).astype(str) + ' months'

CleanedData = CleanedData.drop(index=0).reset_index(drop=True)

CleanedData['Release Date'] = pd.to_datetime(CleanedData['Release Date'], errors='coerce')
CleanedData['Discontinued Date'] = pd.to_datetime(CleanedData['Discontinued Date'], errors='coerce')

# Calculate the median lifespan (in days) for the entries where both dates are available
median_lifespan_days = (CleanedData['Discontinued Date'] - CleanedData['Release Date']).median().days

# Fill missing discontinued dates by adding the median lifespan to the release date
CleanedData['Discontinued Date'] = CleanedData['Discontinued Date'].fillna(CleanedData['Release Date'] + pd.to_timedelta(median_lifespan_days, unit='D'))

# Displaying the updated dataframe
CleanedData[['Model', 'Release Date', 'Discontinued Date']].head()


csv_file_path = 'Cleaned_Apple_Data.csv'
CleanedData.to_csv(csv_file_path, index=False)

# Providing the path to the user
csv_file_path

print(CleanedData)