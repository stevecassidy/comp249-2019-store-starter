#  Copyright (c) 2019.  Steve Cassidy, Department of Computing, Macquarie University

import unittest
import model
import dbschema


class ModelTests(unittest.TestCase):

    def setUp(self):

        # init an in-memory database
        self.db = dbschema.connect(':memory:')
        dbschema.create_tables(self.db)
        self.products = dbschema.sample_data(self.db)

    def test_product_list(self):
        """Test whether we can generate a list of products"""

        products = model.product_list(self.db)

        self.assertEqual(len(self.products), len(products))

        # check that all products are in the result
        names = [p['name'] for p in products]

        for product in self.products.keys():
            self.assertIn(product, names)

    def test_product_list_category(self):
        """Test whether we can generate a list of products in a given category"""

        products = model.product_list(self.db, category="men")

        self.assertEqual(6, len(products))

        # check that all products are in the result
        names = [p[1] for p in products]
        for product in self.products.keys():
            if self.products[product]['category'] == 'men':
                self.assertIn(product, names)

    def test_product_get(self):
        """Test whether we can retrieve a product from it's id"""

        product =  self.products['Yellow Wool Jumper']
        result = model.product_get(self.db, product['id'])

        # check a few fields
        self.assertEqual(product['id'], result['id'])
        self.assertEqual(product['name'], result['name'])



if __name__=='__main__':
    unittest.main()
