import pandas as pd
from sqlalchemy import create_engine

# Convert Excel workbook to SQL
EXCEL_DIR = os.environ.get("MASTER_EXCEL")
SQL_PSWD = os.environ.get("MYSQL_ROOT_PASSWORD")
HOST = os.environ.get("LOCAL_HOST")
SQL_DB = os.environ.get("MYSQL_DATABASE")

df = pd.read_excel(EXCEL_DIR)
df.columns = [c.strip().replace(" ", "_").replace("-","_") for c in df.columns]

engine = create_engine(f"mysql+pymysql://root:{SQL_PSWD}@localhost:{HOST}/{SQL_DB}")

df.to_sql("sold_homes", engine, index=False, if_exists="replace")

zip_code = input("Enter zip code: ")
query = f"SELECT PROPERTY_TYPE, ROUND(AVG(PRICE), -4) AS PRICE_AVG FROM sold_homes WHERE ZIP_OR_POSTAL_CODE = '{zip_code}' GROUP BY PROPERTY_TYPE ORDER BY PRICE_AVG DESC"

results = pd.read_sql(query, engine)
results.to_csv("query.csv", index=False)
