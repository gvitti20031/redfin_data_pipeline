import pandas as pd
from sqlalchemy import create_engine

# Convert Excel workbook to SQL
df = pd.read_excel("/Users/gvitti/Desktop/Work/Data Capstone/Redfin_SD_Data.xlsx")
df.columns = [c.strip().replace(" ", "_").replace("-","_") for c in df.columns]

engine = create_engine("mysql+pymysql://root:redf_n0c4pstn@localhost:3307/redfin_db")

df.to_sql("sold_homes", engine, index=False, if_exists="replace")

zip_code = input("Enter zip code: ")
query = f"SELECT PROPERTY_TYPE, ROUND(AVG(PRICE), -4) AS PRICE_AVG FROM sold_homes WHERE ZIP_OR_POSTAL_CODE = '{zip_code}' GROUP BY PROPERTY_TYPE ORDER BY PRICE_AVG DESC"

results = pd.read_sql(query, engine)
results.to_csv("query.csv", index=False)
