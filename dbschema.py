import csv
import random
import hashlib
import sqlite3
import os

# the name of our database file
DATABASE_NAME = 'shop.db'


def connect(database=DATABASE_NAME):
    """Return a database connection, by default to
    the configured DATABASE_NAME
    Ensure that the connection is configured to return Row objects
    rather than tuples from queries"""

    c = sqlite3.connect(database)
    c.row_factory = sqlite3.Row

    return c


def create_tables(db):
    """Create and initialise the database tables
    This will have the effect of overwriting any existing
    data."""

    sql = """

    DROP TABLE IF EXISTS sessions;
    CREATE TABLE sessions (
            sessionid text unique primary key,
            data text
    );
    
    DROP TABLE IF EXISTS products;
    CREATE TABLE products (
            id integer unique primary key autoincrement,
            name text,
            description text,
            image_url text,
            category text,
            inventory integer,
            unit_cost number
            );
    """

    db.executescript(sql)
    db.commit()


# sample data from https://github.com/shopifypartners/product-csvs/blob/master/apparel.csv

def sample_data(db):
    """Generate some sample data for testing the web
    application. Erases any existing data in the
    database
    Returns the list of users and the list of positions
    that are inserted into the database"""


    cursor = db.cursor()
    cursor.execute("DELETE FROM products")

    # read sample product data from apparel.csv
    products = {}
    id = 0
    first = True  # flag
    sql = "INSERT INTO products (id, name, description, image_url, category, inventory, unit_cost) VALUES (?, ?, ?, ?, ?, ?, ?)"
    with open(os.path.join(os.path.dirname(__file__), 'apparel.csv')) as fd:
        reader = csv.DictReader(fd)
        for row in reader:
            if row['Title'] is not '':
                if first:
                    inv = 0  # inventory of first item (Ocean Blue Shirt) is zero
                    first = False
                else:
                    inv = int(random.random()*100)
                cost = int(random.random()*200) + 0.95
                description = "<p>" + row['Body (HTML)'] + "</p>"
                data = (id, row['Title'], description, row['Image Src'], row['Tags'], inv, cost)
                cursor.execute(sql, data)
                products[row['Title']] = {'id': id, 'name': row['Title'], 'description': description, 'category': row['Tags'], 'inventory': inv, 'unit_cost': cost}
                id += 1

    db.commit()

    return products


def dump_database(db, table):
    """Print out a dump of the database for debugging purposes"""

    print("TABLE: ", table)
    cursor = db.cursor()
    cursor.execute('select * from %s' % table)
    for row in cursor:
        print(dict(row))
    print("--------------")


if __name__=='__main__':
    # if we call this script directly, create the database and make sample data

    db = connect(DATABASE_NAME)
    create_tables(db)
    sample_data(db)

    dump_database(db, "products")
