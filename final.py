import pandas as pd
import re
import numpy as np
from datetime import date
import plotly.express as px

excelFile = pd.ExcelFile(r"SeedUnofficialAppleData.xlsx")
sheetNames = excelFile.sheet_names

data = pd.read_excel(r"SeedUnofficialAppleData.xlsx", sheet_name='Sheet1')

#renaming columns
data.columns = ['Model', 'OS Version', 'Release Date', 'Discontinued Date', 
                      'Support End Date', 'Final OS Version', 'Lifespan', 
                      'Support Min', 'Launch Price']


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

CleanedData['Model'] = CleanedData['Model'].str.split('/').explode('Model').reset_index(drop=True)
print(CleanedData)
    
#function to call convertToMonths function
def convertLifeSpan(x):
    # Convert to months if it's a string
    if isinstance(x, str):
        return ConvertToMonths(x) 
    else:
         # Return None for non-string values
        return None

def averageLaunchPrices(input):
    splitNumbers = re.split(r'\D',str(input))
    numbersList = []
    for sn in splitNumbers:
        if sn != '' :
            numbersList.append(int(sn))
    return str(int(sum(numbersList)/len(numbersList)))

    
CleanedData['Lifespan'] = CleanedData['Lifespan'].apply(convertLifeSpan)
CleanedData['Support Min'] = CleanedData['Support Min'].apply(convertLifeSpan)

#Removing decimal and adding 'months' at the end
CleanedData['Lifespan'] = CleanedData['Lifespan'].fillna(0).astype(int).astype(str) + ' months'
CleanedData['Support Min'] = CleanedData['Support Min'].fillna(0).astype(int).astype(str) + ' months'

CleanedData['Launch Price'] = list(CleanedData['Launch Price'].map(averageLaunchPrices))

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

#print(CleanedData)
changepriceovertime = px.scatter(CleanedData, 
                  x="Release Date", 
                  y="Launch Price", 
                  text="Model",
                  title="Change in iPhone Price Over Time", 
                  labels={"Release Date": "Release Date", "Launch Price": "Launch Price", "Model":"Model"})
changepriceovertime.update_traces(textposition='top center')

changepriceovertime.write_html('changepriceovertime.html')

lifespan = px.scatter(CleanedData, 
                  x="Launch Price", 
                  y="Lifespan", 
                  title="Change in iPhone lifespan with price", 
                  labels={"Lifespan": "Lifespan", "Launch Price": "Launch Price", "Model":"Model"})
lifespan.update_traces(textposition='top center')

lifespan.write_html('changelifeoverprice.html')

support = px.scatter(CleanedData, 
                  x="Support End Date", 
                  y="Lifespan", 
                  title="iPhone Lifespan vs Support", 
                  labels={"Lifespan": "Lifespan", "Support End Date": "Support End Date", "Model":"Model"})
support.update_traces(textposition='top center')

support.write_html('lifevssupport.html')


support2 = px.scatter(CleanedData, 
                  x="Support Min", 
                  y="Lifespan", 
                  title="iPhone Lifespan vs Support Minimum", 
                  labels={"Lifespan": "Lifespan", "Support Min": "Support Minimum", "Model":"Model"})
support2.update_traces(textposition='top center')

support2.write_html('lifevssupportmin.html')

priceOS = px.scatter(CleanedData, 
                  x="OS Version", 
                  y="Launch Price", 
                  title="iPhone Price vs OS Version", 
                  text="Model",
                  labels={"OS Version": "OS Version", "Launch Price": "Launch Price", "Model":"Model"})
priceOS.update_traces(textposition='top center')

priceOS.write_html('priceOS.html')

priceFinalOS = px.scatter(CleanedData, 
                  x="Final OS Version", 
                  y="Launch Price", 
                  title="iPhone Price vs Final OS Version", 
                  text="Model",
                  labels={"Final OS Version": "Final OS Version", "Launch Price": "Launch Price", "Model":"Model"})
priceFinalOS.update_traces(textposition='top center')

priceFinalOS.write_html('priceFinalOS.html')

startOSfinalOS = px.scatter(CleanedData, 
                  x="Final OS Version", 
                  y="OS Version", 
                  title="Start OS Version vs Final OS Version", 
                  text="Model",
                  labels={"Final OS Version": "Final OS Version", "OS Version": "OS Version", "Model":"Model"})
startOSfinalOS.update_traces(textposition='top center')

startOSfinalOS.write_html('startOSFinalOS.html')