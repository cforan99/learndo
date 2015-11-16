from selenium import webdriver
import unittest

class TestClassList(unittest.TestCase):
    """Function tests for the forms on the class lists page"""

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(10)
        self.browser.get('http://localhost:5000/login')
        username = self.browser.find_element_by_name('username')
        password = self.browser.find_element_by_name('password')
        btn = self.browser.find_element_by_id("login-button")
        
        username.send_keys("teachertest")
        password.send_keys("test")
        btn.click()

    def tearDown(self):
        self.browser.get('http://localhost:5000/logout')
        self.browser.quit()

    def test_did_display(self):
        self.browser.get('http://localhost:5000/teacher/0/classes')
        heading = self.browser.find_element_by_id("your-classes")
        self.assertIn("Your classes", heading.text)

    def test_create_class(self):
        """After adding, if the class name appears on the page, it has been added to the db."""
        self.browser.get('http://localhost:5000/teacher/0/classes')
        textfield = self.browser.find_element_by_name('class_name')
        textfield.send_keys("Test Class")

        submit = self.browser.find_element_by_id("create-class")
        submit.click()

        listing = self.browser.find_element_by_id("class-list")
        self.assertIn("Test Class", listing.text)

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

