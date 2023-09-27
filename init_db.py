import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, Date, ForeignKey

#PROD
DATABASE_URI = 'mysql://root:5dqHXLEdS6Ci89wI0gLe@containers-us-west-44.railway.app:6756/railway'

#DEV
# DATABASE_URI = 'sqlite:///C:/Users/u070501/Documents/Phyton/pythonflaskhbca/Project BCAFlaskh/project.db'

engine = create_engine(DATABASE_URI, echo=True)
metadata = MetaData()

accounts = Table('accounts', metadata,
                 Column('account_id', Integer, primary_key=True),
                 Column('customer_name', String),
                 Column('balance', Integer),
                 Column('type', String)
)

transactions = Table('transactions', metadata,
                 Column('transaction_id', Integer, primary_key=True),
                 Column('account_id', Integer, ForeignKey('accounts.account_id', ondelete='NO ACTION')),
                 Column('amount', Integer),
                 Column('date', Date),
                 Column('type', String)
)

metadata.create_all(engine)

print("Database Okeeee")