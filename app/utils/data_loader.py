import pandas as pd
from sqlalchemy import create_engine
from config.settings import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

def load_data():
    # Create the connection string
    connection_string = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    
    # Create the engine
    engine = create_engine(connection_string)
    
    # Load companies data
    companies_df = pd.read_sql_table('companies', engine)
    
    # Convert date columns
    companies_df['registered_date'] = pd.to_datetime(companies_df['registered_date'])
    
    # Convert numeric columns
    numeric_columns = ['registered_capital', 'company_value']
    companies_df[numeric_columns] = companies_df[numeric_columns].apply(pd.to_numeric, errors='coerce')
    
    # Load projects data (assuming it's still in the projects table)
    projects_df = pd.read_sql_table('projects', engine)
    
    # Load financial data
    financial_df = pd.read_sql_table('financial_data', engine)
    
    # Convert financial data numeric columns
    financial_numeric_columns = ['revenue', 'profit_loss', 'tax_expense', 'asset']
    financial_df[financial_numeric_columns] = financial_df[financial_numeric_columns].apply(pd.to_numeric, errors='coerce')
    
    print(f"Loaded {len(companies_df)} companies, {len(projects_df)} projects, and {len(financial_df)} financial records")
    print(f"Companies columns: {companies_df.columns.tolist()}")
    print(f"Projects columns: {projects_df.columns.tolist()}")
    print(f"Financial columns: {financial_df.columns.tolist()}")
    
    return companies_df, projects_df, financial_df

def get_company_details(companies_df, registered_no):
    company = companies_df[companies_df['registered_no'] == registered_no].iloc[0]
    return {
        'registered_no': company['registered_no'],
        'company_name_thai': company['company_name_thai'],
        'company_name_english': company['company_name_english'],
        'address': company['address'],
        'registered_date': company['registered_date'],
        'status': company['status'],
        'registered_type': company['registered_type'],
        'registered_capital': company['registered_capital'],
        'company_value': company['company_value']
    }