"""
Database model for Online Store

Provides functions to access the database
"""


def product_get(db, id):
    """Return the product with the given id or None if
    it can't be found.
    Returns a sqlite3.Row object"""

    sql = """SELECT id, name, description, category, image_url, unit_cost, inventory FROM products WHERE id=?"""
    cur = db.cursor()
    cur.execute(sql, (id,))

    return cur.fetchone()


def product_list(db, category=None):
    """Return a list of products, if category is not None, return products from
    that category. Results are returned in no particular order.
    Returns a list of tuples (id, name, description, category, image_url, unit_cost, inventory)"""

    cur = db.cursor()

    if category:
        sql = """SELECT id, name, description, category, image_url, unit_cost, inventory 
        FROM products WHERE category = ?
        """
        cur.execute(sql, (category,))
    else:
        sql = 'SELECT id, name, description, category, image_url, unit_cost, inventory FROM products'
        cur.execute(sql)

    return cur.fetchall()

