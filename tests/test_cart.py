#  Copyright (c) 2019.  Steve Cassidy, Department of Computing, Macquarie University
import unittest
import session
import dbschema
import model

from bottle import request


class CartTests(unittest.TestCase):

    def setUp(self):

        # init an in-memory database
        self.db = dbschema.connect(':memory:')
        dbschema.create_tables(self.db)
        self.products = dbschema.sample_data(self.db)

    def test_get_cart_contents(self):
        """We can get the contents of the shopping cart"""

        # first need to force the creation of a session and
        # add the cookie to the request
        sessionid = session.get_or_create_session(self.db)
        self.assertIsNotNone(sessionid)
        request.cookies[session.COOKIE_NAME] = sessionid

        # initial cart should be empty
        cart = session.get_cart_contents(self.db)
        self.assertEqual([], cart)

        # now add something to the cart
        for pname in ['Yellow Wool Jumper', 'Ocean Blue Shirt']:
            product =  self.products[pname]
            session.add_to_cart(self.db, product['id'], 1 )

        cart = session.get_cart_contents(self.db)
        self.assertEqual(2, len(cart))

        # check that all required fields are in the every cart entry
        for entry in cart:
            self.assertIn('id', entry)
            self.assertIn('name', entry)
            self.assertIn('quantity', entry)
            self.assertIn('cost', entry)
