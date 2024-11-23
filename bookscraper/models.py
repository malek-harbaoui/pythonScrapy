from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Define the Base
Base = declarative_base()

# Define the Book model
class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    upc = Column(String(50))
    product_type = Column(String(100))
    price_excl_tax = Column(Float)
    price_incl_tax = Column(Float)
    tax = Column(Float)
    availability = Column(String(50))
    num_reviews = Column(Integer)
    stars = Column(String(50))
    category = Column(String(100))
    description = Column(Text)
    price = Column(Float)

    def __repr__(self):
        return f"<Book(title={self.title}, price={self.price})>"

# Create an SQLite engine that connects to a local database file
engine = create_engine('sqlite:///books.db', echo=True)  # SQLite connection (books.db)

# Create tables in the database
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Now you can start interacting with the database using `session`
