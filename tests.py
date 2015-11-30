from selenium import webdriver
import unittest
from server import app
import doctest
from model import db, User, Class
from helper import add_class

def load_tests(loader, tests, ignore):
    """Also run our doctests and file-based doctests."""

    # tests.addTests(doctest.DocTestSuite(server))
    tests.addTests(doctest.DocFileSuite("tests.txt"))
    return tests


class TestRoutes(unittest.TestCase):
    """Integration tests for Flask routes"""

    def test_home_if_logged_out(self):
        self.app = app.test_client()
        result = self.app.get('/')
        self.assertIn('Username', result.data)


class TestClassList(unittest.TestCase):
    """Function tests for the forms on the class lists page"""

    @classmethod
    def setUpClass(cls):
        """Open webdriver and sign in"""
        cls.browser = webdriver.Firefox()
        cls.browser.implicitly_wait(10)
        cls.browser.get('http://localhost:5000/')
        username = cls.browser.find_element_by_name('username')
        password = cls.browser.find_element_by_name('password')
        btn = cls.browser.find_element_by_id("login-button")
        
        username.send_keys("teachertest")
        password.send_keys("test")
        btn.click()


    @classmethod
    def tearDownClass(cls):
        """Sign out and close browser"""
        cls.browser.get('http://localhost:5000/logout')
        cls.browser.quit()


    def test_did_display(self):
        """Checks to see if the class list loaded."""
        self.browser.get('http://localhost:5000/teacher/0/classes')
        heading = self.browser.find_element_by_id("my-classes")
        self.assertIn("My classes", heading.text)

    def test_create_class(self):
        """After adding and refreshing, if the class name appears on the page, 
        it has been added to the db."""

        self.browser.get('http://localhost:5000/teacher/0/classes')
        btn = self.browser.find_element_by_id('new-class')
        btn.click()

        textfield = self.browser.find_element_by_name('class_name')
        textfield.send_keys("Test Class")

        submit = self.browser.find_element_by_id("new-class-button")
        submit.click()

        self.browser.refresh()

        listing = self.browser.find_element_by_id("class-list")
        self.assertIn("Test Class", listing.text)

    def test_remove_class(self):
        """After clicking the delete button and the confirmation button in the 
        pop up menu, a flash message should appear if the class has been deleted 
        from the db. That class will have been removed from the DOM."""

        delete_buttons = self.browser.find_elements_by_class_name("delete_class")
        delete_buttons[0].click()

        confirm = self.browser.find_element_by_id("remove")
        confirm.click()

        buttons_after = self.browser.find_elements_by_class_name("delete_class")

        flash = self.browser.find_element_by_id("flash")
        self.assertIn("has been deleted", flash.text)

        self.assertTrue(len(buttons_after) == len(delete_buttons)-1)


if __name__ == "__main__":
    unittest.main()

