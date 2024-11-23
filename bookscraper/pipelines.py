from itemadapter import ItemAdapter
from jmespath.ast import field
from twisted.python.compat import items

class BookscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        ## Strip all whitespaces from strings
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name !='description':
                value = adapter.get(field_name)
                adapter[field_name] = value[0].strip()


        ## Category & Product Type --> to lowercase
        lowercase_keys = ['category', 'product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key] = value.lower()


        ## Price convert --> to float
        price_keys = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            value = value.replace('£', '')
            adapter[price_key] = float(value)

        ## Availability --> extract number of books in stock
        availability_string = adapter.get('availability')
        split_string_array = availability_string.split('(')
        if len(split_string_array) < 2:
            adapter['availability'] = 0
        else:
            availability_array = split_string_array[1].split(' ')
            adapter['availability'] = int(availability_array[0])

        ## Reviews --> convert string to number
        num_reviews_string = adapter.get('num_reviews')
        adapter['num_reviews'] = int(num_reviews_string)

        ## Stars --> convert text to number
        stars_string = adapter.get('stars')
        split_stars_array = stars_string.split(' ')
        stars_next_value = split_stars_array[1].lower()
        if stars_next_value == "zero":
            adapter['stars'] = 0
        elif stars_next_value == "one":
            adapter['stars'] = 1
        elif stars_next_value == "two":
            adapter['stars'] = 2
        elif stars_next_value == "three":
            adapter['stars'] = 3
        elif stars_next_value == "four":
            adapter['stars'] = 4
        elif stars_next_value == "five":
            adapter['stars'] = 5


        return item


import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bookscraper.models import Book, Base  # Import your Book model

class SaveToSQLitePipeline:

    def __init__(self):
        # Create the SQLite database connection using SQLAlchemy
        self.engine = create_engine('sqlite:///books.db', echo=True)  # SQLite connection string
        # Create all tables if they don't exist
        Base.metadata.create_all(self.engine)

        # Create a sessionmaker bound to the engine
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def process_item(self, item, spider):
        """
        Process each scraped item and store it in the SQLite database.
        """
        try:
            description = item.get('description', '')
            if isinstance(description, tuple) or isinstance(description, list):
                description = ' '.join(description)
            
            # Create a new Book instance from the scraped item
            book = Book(
                url=item['url'],
                title=item['title'],
                upc=item['upc'],
                product_type=item['product_type'],
                price_excl_tax=item['price_excl_tax'],
                price_incl_tax=item['price_incl_tax'],
                tax=item['tax'],
                availability=item['availability'],
                num_reviews=item['num_reviews'],
                stars=item['stars'],
                category=item['category'],
                description=description,
                price=item['price']
            )
            
            # Add the book to the session and commit the transaction
            self.session.add(book)
            self.session.commit()

            return item
        except Exception as e:
            # Handle exceptions (e.g., integrity errors, connection issues)
            self.session.rollback()  # Rollback the transaction if there's an error
            spider.logger.error(f"Error saving item to database: {e}")
            return None

    def close_spider(self, spider):
        """
        This method is called when the spider closes.
        Ensures the session is properly closed.
        """
        self.session.close()


















