import pandas as pd
import os
from sqlalchemy import create_engine
import logging
import time

# Corrected logging configuration with UTF-8 encoding
logging.basicConfig(
    filename='logs/ingestion_db.log',
    level=logging.DEBUG,
    # Ensure the format key for message is '%(message)s'
    format='%(asctime)s-%(levelname)s-%(message)s', 
    filemode='a',
    encoding='utf-8' # Ensures emojis can be written to the log file
)
# Note: In the provided traceback, it seems the code calling logging.info was 
# using a different logger object named 'logger' which might have 
# caused the 'messgae' KeyError in a local environment where the code wasn't 
# fully consistent. For the code provided above, use 'logging.info(...)'.
# If you are using a separate logger object, ensure it's defined correctly.

engine = create_engine("sqlite:///inventory.db")

# ... rest of your functions (ingest_db and load_raw_data)
# Make sure to use 'logging.info' within your functions, 
# not an undefined 'logger.info' as suggested by the traceback:

def ingest_db(df, table_name, engine):
    '''This function will ingest the dataframe into database table'''
    df.to_sql(table_name, con=engine, if_exists='replace',index=False)
    # Use 'logging.info' here
    logging.info(f"✅ Successfully ingested table: {table_name} ({df.shape[0]} rows, {df.shape[1]} cols)")

def load_raw_data():
    '''This function will load the excels as dataframe and ingest into db'''
    start=time.time()
    data_folder = 'data'
    
    for file in os.listdir(data_folder):
        if file.endswith('.xlsx'):  # only rocess excel files
            file_path = os.path.join(data_folder, file)
            df = pd.read_excel(file_path)
            # Use 'logging.info' here
            logging.info(f'📥 Ingesting {file} in db') 
            ingest_db(df, file[:-5],engine)
    end=time.time()
    total_time=(end-start)/60
    logging.info('------------------------Ingestion Complete----------------------------')
    
    logging.info(f'\nTotal Time Taken: {total_time} minutes')
    
if __name__=="__main__":
    load_raw_data()