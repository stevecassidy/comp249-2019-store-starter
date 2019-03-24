import unittest
import sqlite3
import os
from bottle.ext import sqlite
import bottle
import html
from webtest import TestApp
import dbschema
import main
import session
import urllib

DATABASE_NAME = "test.db"
# initialise the sqlite plugin for bottle
main.app.install(sqlite.Plugin(dbfile=DATABASE_NAME))
bottle.debug()

# make sure bottle looks for templates in the main directory, not this one
bottle.TEMPLATE_PATH = [os.path.join(os.path.dirname(__file__), p) for p in ['../', '../views/']]


class FunctionalTests(unittest.TestCase):

    def setUp(self):
        self.app = TestApp(main.app)
        self.db = dbschema.connect(DATABASE_NAME)
        dbschema.create_tables(self.db)
        self.products = dbschema.sample_data(self.db)

    def tearDown(self):
        self.db.close()
        os.unlink(DATABASE_NAME)

    def test_home_page_links(self):
        """Home page contains links to Home and View Cart"""

        response = self.app.get('/')

        # should find at least one link to home
        links = response.html.findAll('a', href='/')
        self.assertGreaterEqual(len(links), 1, "No links to '/' found in response")

        links = response.html.findAll('a', href='/cart')
        self.assertGreaterEqual(len(links), 1, "No links to '/cart' found in response")

    def test_home_page_product_names(self):
        """Home page should contain the names of all products in
        the database
        """

        response = self.app.get('/')

        for key in self.products:
            product = self.products[key]
            title = html.escape(product['name'])
            self.assertIn(title, response)

    def test_home_page_product_links(self):
        """Home page contains links to product pages"""

        response = self.app.get('/')

        for key in self.products:
            product = self.products[key]

            # find a link to this product
            links = response.html.findAll('a', href="/product/%s" % product['id'])
            self.assertGreaterEqual(len(links), 1)

    def test_home_page_creates_cookie(self):
        """First request to the home page should return a
        cookie in the response"""

        response = self.app.get('/')
        self.assertIn(session.COOKIE_NAME, self.app.cookies)

    def test_product_page_creates_cookie_with_path(self):
        """A request to a product page should create a cookie
        and the path should be set to /"""

        response = self.app.get('/product/0')

        self.assertIn(session.COOKIE_NAME, self.app.cookies)
        cookie = list(self.app.cookiejar)[0]
        self.assertEqual('/', cookie.path, "cookie path should be set to /")

    def test_product_page(self):
        """Each product has a page at /products/<id> with
        details of the product, the product page contains
        the product name and cost and the description (which may
        contain HTML markup)"""

        for key in self.products:
            product = self.products[key]
            url = "/product/%s" % product['id']
            response = self.app.get(url)

            self.assertEqual(200, response.status_code, "Expected 200 OK response for URL %s" % url)
            self.assertIn(html.escape(product['name']), response)
            self.assertIn(str(product['unit_cost']), response)
            self.assertIn(product['description'], response)

    def test_product_page_not_found(self):
        """Requesting the page for a product id that does not
        exist returns a 404 response"""

        url = "/product/99999"
        response = self.app.get(url, status=404)

        self.assertEqual(404, response.status_code, "Expected 404 Not Found response for URL %s" % url)

    def test_product_page_add_cart_form(self):
        """Each product page should have a form
        to add the product to the shopping cart"""

        for key in self.products:
            product = self.products[key]
            url = "/product/%s" % product['id']
            response = self.app.get(url)
            self.assertEqual(200, response.status_code, "Expected 200 OK response for URL %s" % url)

            # page may have more than one form, but one of them must have the action /cart
            cartform = None
            for idx in response.forms:
                if response.forms[idx].action == '/cart':
                    cartform = response.forms[idx]

            self.assertIsNotNone(cartform, 'Did not find form with action="/cart" in response')

            self.assertEqual(str(product['id']), cartform['product'].value)

    def test_add_to_cart_works(self):
        """If I click on the add to cart button my product
        is added to the shopping cart"""

        product = self.products['Yellow Wool Jumper']
        url = "/product/%s" % product['id']
        response = self.app.get(url)
        self.assertEqual(200, response.status_code, "Expected 200 OK response for URL %s" % url)

        # page may have more than one form, but one of them must have the action /cart
        cart_form = None
        for idx in response.forms:
            if response.forms[idx].action == '/cart':
                cart_form = response.forms[idx]

        self.assertIsNotNone(cart_form, 'Did not find form with action="/cart" in response')

        # fill out the form
        cart_form['quantity'] = 2

        response = cart_form.submit()

        self.assertEqual(302, response.status_code, 'Expected 302 redirect response from cart form submission')
        urlparts = urllib.parse.urlparse(response.headers['Location'])
        location = urlparts[2]
        self.assertEqual('/cart', location, "Expected redirect location header to be /cart")

        # and our product should be in the cart
        cart = session.get_cart_contents(self.db)

        self.assertEqual(1, len(cart))
        self.assertEqual(str(product['id']), cart[0]['id'])
        self.assertEqual(2, cart[0]['quantity'])

    def test_cart_page(self):
        """The page at /cart should show the current contents of the
        shopping cart"""

        product = self.products['Yellow Wool Jumper']
        url = "/product/%s" % product['id']
        response = self.app.get(url)
        self.assertEqual(200, response.status_code, "Expected 200 OK response for URL %s" % url)

        # page may have more than one form, but one of them must have the action /cart
        cart_form = None
        for idx in response.forms:
            if response.forms[idx].action == '/cart':
                cart_form = response.forms[idx]

        self.assertIsNotNone(cart_form, 'Did not find form with action="/cart" in response')

        # fill out the form
        cart_form['quantity'] = 2

        response = cart_form.submit()

        self.assertEqual(302, response.status_code, 'Expected 302 redirect response from cart form submission')

        # and our product should be in the cart
        cart = session.get_cart_contents(self.db)

        response = self.app.get('/cart')

        # look for the product name in the returned page
        self.assertIn(product['name'], response)


if __name__=='__main__':

    unittest.main()
