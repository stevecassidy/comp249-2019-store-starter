import unittest
from bottle import request, response
from http.cookies import SimpleCookie

import session
import dbschema


class SessionTests(unittest.TestCase):

    def setUp(self):

        # init an in-memory database
        self.db = dbschema.connect(':memory:')
        dbschema.create_tables(self.db)
        self.products = dbschema.sample_data(self.db)

    def tearDown(self):

        # must remove our fake cookie from the global request
        if session.COOKIE_NAME in request.cookies:
            del request.cookies[session.COOKIE_NAME]

    @staticmethod
    def get_cookie_value(cookiename):
        """Get the value of a cookie from the bottle response headers"""

        headers = response.headerlist
        for h,v in headers:
            if h == 'Set-Cookie':
                cookie = SimpleCookie(v)
                if cookiename in cookie:
                    return cookie[cookiename].value

        return None

    def test_get_or_create_session(self):
        """The get_or_create_session procedure creates a new
        session if none is present or returns an existing one"""

        sessionid = session.get_or_create_session(self.db)

        self.assertIsNotNone(sessionid)

        # set sessionid cookie in request
        request.cookies[session.COOKIE_NAME] = sessionid
        # second call, should get session info from request cookie
        sessionid1 = session.get_or_create_session(self.db)

        self.assertEqual(sessionid, sessionid1)

        cookieval = self.get_cookie_value(session.COOKIE_NAME)
        self.assertEqual(sessionid, cookieval)

    def test_session_bad_cookie(self):
        """If the cookie we receive is not a valid session key, it
        should be ignored and a new session created"""

        # set sessionid cookie in request
        invalidkey = "InvalidSessionKey"
        request.cookies[session.COOKIE_NAME] = invalidkey

        sessionid = session.get_or_create_session(self.db)

        self.assertNotEqual(invalidkey, sessionid)

        cookieval = self.get_cookie_value(session.COOKIE_NAME)
        self.assertEqual(sessionid, cookieval)




if __name__=='__main__':
    unittest.main()


