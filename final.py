import pandas as pd
import re

excelFile = pd.ExcelFile(r"SeedUnofficialAppleData.xlsx")
sheetNames = excelFile.sheet_names

data = pd.read_excel(r"SeedUnofficialAppleData.xlsx", sheet_name='Sheet1')

#renaming columns
data.columns = ['Model', 'OS Version', 'Release Date', 'Discontinued Date', 
                      'Support End Date', 'Final OS Version', 'Lifespan', 
                      'Support Min', 'Launch Price']

#getting price from the Lauch prices column 
def price(priceStr):
    regex = '\d+'
    prices = re.findall(regex, priceStr)
    return[int(price) for price in prices ]


#function for merging price for multiple rows to 1 row
def mergePrices(df):
    # checking if launch price has '*' and release date is nan
    checkPrice = df['Launch Price'].str.contains(r'\*', na=False) & df['Release Date'].isna().shift(-1)
    
    # Iterate over the checkPrice rows
    for i in df[checkPrice].index:
        # Combine current row's price with the next row's price
        df.loc[i, 'Launch Price'] = str(df.loc[i, 'Launch Price']) + ' ' + str(df.loc[i + 1, 'Launch Price'])

    
    # Drop rows where 'Release Date' is NaN since they are price continuation rows
    df = df.dropna(subset=['Release Date']).reset_index(drop=True)
    
    return df


#initiliazing cleandata calling in merge price function
CleanedData = mergePrices(data)


# Resetting the index for a clean DataFrame
CleanedData.reset_index(drop=True, inplace=True)

#removing rows on Model column it its nan
CleanedData = CleanedData.dropna(subset=['Model'])


#Changing years to months
def ConvertToMonths(lifespan_str):
    years = 0
    months = 0
    
    # Split the string into parts
    parts = lifespan_str.split()
    
    #looping through parts to check year and  months
    for i in range(len(parts)):
        if "year" in parts[i]:
            # Get the number before 'year' and handle potential non-numeric characters
            years_str = ''.join(filter(str.isdigit, parts[i-1]))  # Keep only digits
            years = int(years_str) if years_str else 0  # Convert to int or set to 0 if empty
        elif "month" in parts[i]:
            # Get the number before 'month' and handle potential non-numeric characters
            months_str = ''.join(filter(str.isdigit, parts[i-1]))  # Keep only digits
            months = int(months_str) if months_str else 0  # Convert to int or set to 0 if empty
    
    
    #Converting to months
    return years * 12 + months

#function to call convertToMonths function
def convertLifeSpan(x):
    # Convert to months if it's a string
    if isinstance(x, str):
        return ConvertToMonths(x) 
    else:
         # Return None for non-string values
        return None
    
CleanedData['Lifespan'] = CleanedData['Lifespan'].apply(convertLifeSpan)
CleanedData['Support Min'] = CleanedData['Support Min'].apply(convertLifeSpan)

#Removing decimal and adding 'months' at the end
CleanedData['Lifespan'] = CleanedData['Lifespan'].fillna(0).astype(int).astype(str) + ' months'
CleanedData['Support Min'] = CleanedData['Support Min'].fillna(0).astype(int).astype(str) + ' months'


#converting release date and discontinued date to datetime
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