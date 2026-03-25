import pandas as pd
import glob
import os
DEFAULT_PATH = "/Users/gvitti/Downloads/"

data_to_analyze = input("Type the name of the folder you want to analyze: ").strip()
input_folder = os.path.join(DEFAULT_PATH, data_to_analyze)
output_folder = f"/Users/gvitti/Desktop/Work/Data Capstone/{data_to_analyze}Final"

os.makedirs(output_folder, exist_ok=True)

all_files = glob.glob(os.path.join(input_folder, "*.csv"))

# Find files in a directory
for filename in all_files:
    data = pd.read_csv(filename)
    data = data[~data["SALE TYPE"].str.contains("In accordance with local MLS rules", case=False, na=False)]

    # Keep index 20, URLs, for better data analysis
    columns_to_drop = [0, 10, 14] + list(range(16,20)) + list(range(21,27))
    data.drop(data.columns[columns_to_drop], axis=1, inplace=True)
    data = data[~data["PROPERTY TYPE"].str.contains("Multi-Family", case=False, na=False)]
    data = data[~data["PROPERTY TYPE"].str.contains("Mobile/Manufactured Home", case=False, na=False)]

    # Move URL index next to Address, target index 3
    data.rename(columns={"URL (SEE https://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)": "URL"}, inplace=True)
    columns = list(data.columns)
    columns.insert(3, columns.pop(columns.index("URL")))

    data = data[columns]

    data["SOLD DATE"] = pd.to_datetime(data["SOLD DATE"], format="%B-%d-%Y")
    data["DAYS SINCE"] = (pd.Timestamp.today() - data["SOLD DATE"]).dt.days
    data["SOLD DATE"] = data["SOLD DATE"].dt.strftime("%m/%d/%Y")

    # Send to a CSV file inside a folder
    output_file = os.path.join(output_folder, os.path.basename(filename))
    data.to_csv(output_file, index=False)
