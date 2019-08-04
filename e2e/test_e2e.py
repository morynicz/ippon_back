from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver


class MySeleniumTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        email = 'admin'
        password = 'password'
        self.user = User.objects.create(username='admin', password='password')

        self.selenium.get('%s%s' % ('localhost:4231', '/login/'))
        username_input = self.selenium.find_element_by_name("email")
        username_input.send_keys(email)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(password)
        self.selenium.find_element_by_id('login-login').click()

        self.selenium.implicitly_wait(10)

        self.assertIsNone(self.selenium.find_element_by_id('logout'))

# class E2ETests(test.TestCase):
#     pass
