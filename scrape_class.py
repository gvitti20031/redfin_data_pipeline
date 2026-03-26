from datetime import datetime
import requests
import glob
import os
import pandas as pd
from bs4 import BeautifulSoup
DEFAULT_PATH = os.environ.get("DEF_PATH")
RENOVATION_KEYWORDS = ["fully renovated", "fully remodeled", "fully upgraded", "fully updated", "completely updated", "kitchen and bath remodeled", "turnkey", "turn-key"]
FIXER_KEYWORDS = ["fixer", "fixer upper", "handyman special", "contractor special", "investor special", "needs TLC", "needs updating", "needs TLC",
                  "needs renovation", "needs work", "cosmetic fixer", "renovation opportunity", "great bones", "bring your vision", "priced to sell", "blank canvas", "make it your own"]

data_to_analyze = input("Please enter the folder you would like to analyze: ").strip()
input_folder = os.path.join(DEFAULT_PATH, data_to_analyze)
output_folder = f"{DEFAULT_PATH}{data_to_analyze}Parsed"
os.makedirs(output_folder, exist_ok=True)
all_files = glob.glob(os.path.join(input_folder, "*.csv"))

df_list = []
for filename in all_files:

    input_file = pd.read_csv(filename)
    address_list = input_file.ADDRESS.tolist()
    url_list = input_file.URL.tolist()

    session = requests.Session()
    # Credentials to scrape individual Redfin sites
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    for url in url_list:
        is_renovated = 'N'
        is_fixer = 'N'
        response = session.get(url, headers=headers, timeout=1800)

        # Initialize the web scraper
        soup = BeautifulSoup(response.text, "html.parser")

        # Retrieve listing descriptions for each URL
        desc = soup.select_one("div.remarks")
        listing_desc = desc.get_text(strip=True).lower() if desc else ""

        if any(word in listing_desc for word in RENOVATION_KEYWORDS):
            is_renovated = 'Y'
        if any(word in listing_desc for word in FIXER_KEYWORDS):
            is_fixer = 'Y'

        input_file.loc[input_file["URL"] == url, "RENOVATED?"] = is_renovated
        input_file.loc[input_file["URL"] == url, "FIXER-UPPER?"] = is_fixer

        # Retrieve the date from each URL where the sale date is not already listed
        if pd.isna(input_file.loc[input_file["URL"] == url, "SOLD DATE"].values[0]):
            date = soup.select_one("div.BasicTable__col.date")
            if date:
                date_to_convert = date.get_text()
                parsed_date = datetime.strptime(date_to_convert, "%b %d, %Y")
                input_file.loc[input_file["URL"] == url, "DAYS SINCE"] = (pd.Timestamp.today() - pd.Timestamp(parsed_date)).days
                final_date = f"{parsed_date.month}/{parsed_date.day}/{str(parsed_date.year)[-2:]}"
                input_file["SOLD DATE"] = input_file["SOLD DATE"].astype("object")
                input_file.loc[input_file["URL"] == url, "SOLD DATE"] = final_date
            else:
                input_file.loc[input_file["URL"] == url, "SOLD DATE"] = ""

    # Drop URL column
    input_file.drop(columns="URL", inplace=True)
    df_list.append(input_file)

merged_df = pd.concat(df_list, ignore_index=True)
merged_df.to_csv(f"{output_folder}/merged_df.csv", index=False)
