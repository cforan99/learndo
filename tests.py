from selenium import webdriver
import unittest

class TestClassList(unittest.TestCase):
    """Function tests for the forms on the class lists page"""

    def setUp(self):
        """Open webdriver and sign in"""
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(10)
        self.browser.get('http://localhost:5000/')
        username = self.browser.find_element_by_name('username')
        password = self.browser.find_element_by_name('password')
        btn = self.browser.find_element_by_id("login-button")
        
        username.send_keys("teachertest")
        password.send_keys("test")
        btn.click()

    def tearDown(self):
        """Sign out and close browser"""
        self.browser.get('http://localhost:5000/logout')
        self.browser.quit()

    def test_did_display(self):
        """Checks to see if the class list loaded."""
        self.browser.get('http://localhost:5000/teacher/0/classes')
        heading = self.browser.find_element_by_id("my-classes")
        self.assertIn("My classes", heading.text)

    def test_create_remove_class(self):
        """After adding and refreshing, if the class name appears on the page, it has been added to the db.
        After clicking the delete button and the confirmation button in the pop up menu, a flash message should
        appear if the class has been deleted from the db."""
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

        # remove = self.browser.find_element_by_xpath("#class-list ul li:first button")
        # remove.click()

        # confirm = self.browser.find_element_by_id("remove")
        # confirm.click()

        # self.browser.refresh()

        # flash = self.browser.find_element_by_id("flash")
        # self.assertIn("The class, Test Class, has been deleted", flash.text)


    """Remove student / class"""

    """Add student by username"""

    """Create student account"""

    

if __name__ == "__main__":
    unittest.main()












# new_teacher = User(user_id=0,
#            is_teacher=1,
#            username="teachertest",
#            password="test",
#            email="test@test.com",
#            first_name="Teacher",
#            last_name="Test",
#            display_name="Ms. Test",
#            school="Test School")

