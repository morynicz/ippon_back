import selenium
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver

import ippon


class MySeleniumTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 8923
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self) -> None:
        super(MySeleniumTests, self).setUp()
        self.username = 'admin'
        self.password = 'password'
        self.email= 'admin@amdin.com'
        self.user = User.objects.create_user(username=self.username, password=self.password, email=self.email)

    def log_in(self):
        self.selenium.get('%s%s' % ('localhost:4231', '/login/'))
        self.selenium.implicitly_wait(10)

        username_input = self.selenium.find_element_by_name("email")
        username_input.send_keys(self.username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(self.password)
        self.selenium.implicitly_wait(10)
        self.selenium.find_element_by_id('login-login').click()


    def test_login(self):
        self.log_in()
        # self.selenium.implicitly_wait(100)
        with self.assertRaises(selenium.common.exceptions.NoSuchElementException):
            self.selenium.find_element_by_id("login")

    def test_logout(self):
        self.log_in()
        # self.selenium.implicitly_wait(100)

        print(self.selenium.find_element_by_id('logout'))
        self.selenium.find_element_by_id('logout').click()

        with self.assertRaises(selenium.common.exceptions.NoSuchElementException):
            self.selenium.find_element_by_id("logout")



