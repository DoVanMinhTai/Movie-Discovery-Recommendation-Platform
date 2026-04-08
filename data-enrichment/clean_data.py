from crawl_data import DATA_DIR



DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

ETL_DIR = os.path.join(DATA_DIR, 'etl')

EXTRACTED_DATA_DIR = os.path.join(ETL_DIR, 'extracted')

CLEAN_DATA_DIR = os.path.join(ETL_DIR, 'clean')



df = pd.read_csv(os.path.join(EXTRACTED_DATA_DIR, 'mediacontent.csv'))

df.drop_duplicates(subset=['movieId'], keep='first', inplace=True)

df.to_csv(os.path.join(CLEAN_DATA_DIR, 'mediacontent_clean.csv'), index=False)