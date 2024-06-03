import unittest
from subprocess import Popen
from selenium import webdriver
from selenium.webdriver.common.by import By
import  time


class AppTest(unittest.TestCase):
    BACKEND_NAME = 'backend.py'
    START_URL = 'http://localhost:8000'
    LOGOUT_SIGNATURE = 'Log Out'

    TEST_USERS = (
        ('Alice A.', 'alice_2002@gmail.com', 'aaa'),
        ('Bob B.', 'bob_2001@gmail.com', 'bbb'),
    )

    def setUp(self):
        self.backend_process = Popen(['python', self.BACKEND_NAME])

    def tearDown(self):
        self.backend_process.kill()

    def _prepare_login(self, driver, email, password):
        elem = driver.find_element(By.NAME, 'email')
        elem.clear()
        elem.send_keys(email)
        elem = driver.find_element(By.NAME, 'password')
        elem.clear()
        elem.send_keys(password)

    def _log_in(self, driver, email, password):
        self._prepare_login(driver, email, password)
        driver.find_element(By.XPATH, '//button[.="Log In"]').click()

    def _log_in_test_user(self, driver, user_index=0):
        display_name, email, password = self.TEST_USERS[user_index]
        self._log_in(driver, email, password)

    def _get_editor_elem(self, driver):
        return driver.find_element(By.CLASS_NAME, 'ql-editor')

    def _post_comment(self, driver, plain_text_comment):
        self._get_editor_elem(driver).clear()
        self._get_editor_elem(driver).send_keys(plain_text_comment)
        driver.find_element(By.XPATH, '//button[.="New comment"]').click()

    def _get_all_comments(self, driver):
        comments = []

        for elem in driver.find_elements(By.XPATH, '//div[@id="comments"]/ul/li'):
            comment_text = elem.find_element(By.TAG_NAME, 'span').text
            author = elem.find_element(By.TAG_NAME, 'a').text
            comments.append((comment_text, author))

        return comments

    # Test 2
    def test_signup(self):
        user_name = 'Julia'
        user_email = 'jj@gmail.com'
        password = '0000'

        driver = webdriver.Chrome()
        with driver:
            driver.get(self.START_URL)

            # Test 2.a
            driver.find_element(By.NAME, 'display_name').send_keys(user_name)
            time.sleep(3)
            driver.find_element(By.NAME, 'email').send_keys(user_email)
            time.sleep(3)
            driver.find_element(By.NAME, 'password').send_keys(password)
            time.sleep(3)
            driver.find_element(By.XPATH, '//button[.="Sign Up"]').click()

            self.assertTrue(driver.find_elements(By.XPATH, '//button[.="Log Out"]'))
            raw_text = driver.find_element(By.ID, 'signup-section').text
            #print(raw_text)
            self.assertEqual(raw_text[:-len(self.LOGOUT_SIGNATURE)], user_name)

            # Test 2.b
            driver.find_element(By.XPATH, '//button[.="Log Out"]').click()
            elems = driver.find_elements(By.XPATH, '//button[.="Log In"]')
            self.assertTrue(elems, 'User did not log out')

            # Test 2.c
            #other_display_name = 'Andrew'
            other_password = '2222222222'
            elem = driver.find_element(By.NAME, 'display_name')
            elem.clear()
            elem.send_keys(user_name)
            time.sleep(3)
            elem = driver.find_element(By.NAME, 'email')
            elem.clear()
            elem.send_keys(user_email)
            elem = driver.find_element(By.NAME, 'password')
            elem.clear()
            elem.send_keys(other_password)
            driver.find_element(By.XPATH, '//button[.="Sign Up"]').click()

            elems = driver.find_elements(By.XPATH, '//button[.="Log Out"]')
            self.assertFalse(elems, 'User actually logged in with non unique email')

    #TEST 5
    def test_comment_creation(self):

        EXPECTED_COMMENT_HTML = \
            '<span>Testing <u>comment </u><strong><em>creation </em><s>ri</s>ght</strong> now.</span>'

        def click_style(style_name):
            driver.find_element(By.CLASS_NAME, 'ql-' + style_name).click()

        driver = webdriver.Chrome()
        with driver:
            driver.get(self.START_URL)
            self._log_in_test_user(driver)

            self._get_editor_elem(driver).clear()
            target = self._get_editor_elem(driver)
            target.send_keys('Testing ')
            click_style('underline')
            target.send_keys('comment ')
            click_style('underline')
            click_style('bold')
            click_style('italic')
            target.send_keys('creation ')
            click_style('italic')
            click_style('strike')
            target.send_keys('ri')
            click_style('strike')
            target.send_keys('ght')
            click_style('bold')
            target.send_keys(' now.')
            driver.find_element(By.XPATH, '//button[.="New comment"]').click()
            last_comment_e = driver.find_element(By.XPATH, '//div[@id="comments"]/ul/li[last()]/span')
            time.sleep(5)
            self.assertEqual(EXPECTED_COMMENT_HTML, last_comment_e.get_attribute('outerHTML'))


    def open_driver(self):
        return webdriver.Chrome()

    def remove_comment(self, driver, index):
        driver.find_elements(By.XPATH, '//div[@id="comments"]/ul/li/span[2][.="Remove"]')[index].click()

    # Test 8
    def test_8_multiuser(self):
        with self.open_driver() as driver1:
            # Test 8.a
            driver1.get(self.START_URL)
            self._log_in(driver1, "alice_2002@gmail.com", "aaa")
            self._post_comment(driver1, "Comment from ALICE №1")

            with self.open_driver() as driver2:
                # Test 8.b
                driver2.get(self.START_URL)
                self._log_in(driver2, "bob_2001@gmail.com", "bbb")
                self._post_comment(driver2, "Comment from BOB №1")
                self.assertEqual(self._get_all_comments(driver2)[-2:],
                                 [("Comment from ALICE №1", 'Alice A.'),
                                  ("Comment from BOB №1", 'Bob B.')],
                                 "Comments are wrong")

                # Test 8.c
                self._post_comment(driver1, "Comment from ALICE №2")
                self.assertEqual(self._get_all_comments(driver1)[-3:],
                                 [("Comment from ALICE №1", 'Alice A.'),
                                  ("Comment from BOB №1", 'Bob B.'),
                                  ("Comment from ALICE №2", 'Alice A.')],
                                 "Comments are wrong")
                time.sleep(7)

if __name__ == '__main__':
    unittest.main()
