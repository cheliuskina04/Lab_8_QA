import unittest
from subprocess import Popen

from selenium import webdriver
from selenium.webdriver.common.by import By


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

    def test_anonymous(self):
        driver = webdriver.Chrome()
        with driver:
            driver.get(self.START_URL)

            # Test 1.a
            elems = driver.find_elements(By.XPATH, '//h1[.="Is this a good way to process input?"]')
            self.assertTrue(elems, 'Question header is absent')

            # Test 1.b
            elems = driver.find_elements(By.XPATH, '//div[@id="question"]/pre[text()!=""]')
            self.assertTrue(elems, 'Question body is empty')

            # Test 1.c
            elems = driver.find_elements(By.XPATH, '//div[@id="comments"]/ul/li')
            self.assertTrue(len(elems) == 2, 'The number of comments is not 2')

            # First way
            elems = driver.find_elements(By.XPATH,
                                         '//div[@id="comments"]/ul/li[1][span="Test comment 1"][a="Alice A."]')
            self.assertTrue(elems, 'Alice comment isn`t correct')
            # Same way for Bob B.

            # Second way
            comments = (
                ('Test comment 1', 'Alice A.'),
                ('Test comment 2', 'Bob B.'),
            )

            for comment, elem in zip(comments, driver.find_elements(By.XPATH, '//div[@id="comments"]/ul/li')):
                comment_text = elem.find_element(By.TAG_NAME, 'span').text
                author = elem.find_element(By.TAG_NAME, 'a').text
                self.assertEqual(comment, (comment_text, author), 'Comment does not match')
                print(comment_text, author)

            # Test 1.d
            elems = driver.find_elements(By.XPATH, '//button[.="Sign Up"]')
            self.assertTrue(elems, 'Sign up button is missing')

            elems = driver.find_elements(By.XPATH, '//button[.="Log In"]')
            self.assertTrue(elems, 'Log in button is missing')

            # Test 1.e
            elems = driver.find_elements(By.XPATH,
                                         '//div[label[1][.="Display Name"][following-sibling::input[1][@name="display_name"]]]')
            self.assertTrue(elems, 'Incorrect Display Name section')

    # Test 2
    def test_signup(self):
        display_name = 'Arseniy'
        email = 'test@gmail.com'
        password = '1111'

        driver = webdriver.Chrome()
        with driver:
            driver.get(self.START_URL)

            # Test 2.a
            driver.find_element(By.NAME, 'display_name').send_keys(display_name)
            driver.find_element(By.NAME, 'email').send_keys(email)
            driver.find_element(By.NAME, 'password').send_keys(password)
            driver.find_element(By.XPATH, '//button[.="Sign Up"]').click()

            self.assertTrue(driver.find_elements(By.XPATH, '//button[.="Log Out"]'))
            raw_text = driver.find_element(By.ID, 'signup-section').text
            self.assertEqual(raw_text[:-len(self.LOGOUT_SIGNATURE)], display_name)

            # Test 2.b
            driver.find_element(By.XPATH, '//button[.="Log Out"]').click()
            elems = driver.find_elements(By.XPATH, '//button[.="Log In"]')
            self.assertTrue(elems, 'User did not log out')

            # Test 2.c
            other_display_name = 'Andrew'
            other_password = '2222222222'
            elem = driver.find_element(By.NAME, 'display_name')
            elem.clear()
            elem.send_keys(other_display_name)
            elem = driver.find_element(By.NAME, 'email')
            elem.clear()
            elem.send_keys(email)
            elem = driver.find_element(By.NAME, 'password')
            elem.clear()
            elem.send_keys(other_password)
            driver.find_element(By.XPATH, '//button[.="Sign Up"]').click()

            elems = driver.find_elements(By.XPATH, '//button[.="Log Out"]')
            self.assertFalse(elems, 'User actually logged in with non unique email')

    def test_login(self):
        display_name, email, password = self.TEST_USERS[1]

        driver = webdriver.Chrome()
        with driver:
            driver.get(self.START_URL)

            driver.find_element(By.NAME, 'email').send_keys(email)
            driver.find_element(By.NAME, 'password').send_keys(password)
            driver.find_element(By.XPATH, '//button[.="Log In"]').click()

            raw_text = driver.find_element(By.ID, 'signup-section').text
            self.assertEqual(raw_text[:-len(self.LOGOUT_SIGNATURE)], display_name)

            driver.find_element(By.XPATH, '//button[.="Log Out"]').click()

            other_password = 'incorrect'
            elem = driver.find_element(By.NAME, 'password')
            elem.clear()
            elem.send_keys(other_password)
            driver.find_element(By.XPATH, '//button[.="Log In"]').click()

            elems = driver.find_elements(By.XPATH, '//button[.="Log Out"]')
            self.assertFalse(elems, 'User actually logged in with incorrect password')

    def test_screenshot(self):

        JS = """
        var elem = document.getElementById('editor-section');
        elem.style.borderColor = "red";
        elem.style.borderStyle = "solid";
        """

        driver = webdriver.Chrome()
        with driver:
            driver.get(self.START_URL)
            self._log_in_test_user(driver)

            elem = driver.find_element(By.ID, 'editor-section')
            self.assertTrue(elem, 'Editor section is not present')

            driver.execute_script(JS)
            driver.save_screenshot('screenshot.png')

    def test_comment_creation(self):
        EXPECTED_COMMENT_HTML = \
            '<span>This <strong>comment </strong><em>is </em><s>un</s>necessary.<u> Honest.</u></span>'

        def click_style(style_name):
            driver.find_element(By.CLASS_NAME, 'ql-' + style_name).click()

        driver = webdriver.Chrome()
        with driver:
            driver.get(self.START_URL)
            self._log_in_test_user(driver)

            self._get_editor_elem(driver).clear()
            target = self._get_editor_elem(driver)
            target.send_keys('This ')
            click_style('bold')
            target.send_keys('comment ')
            click_style('bold')
            click_style('italic')
            target.send_keys('is ')
            click_style('italic')
            click_style('strike')
            target.send_keys('un')
            click_style('strike')
            target.send_keys('necessary.')
            click_style('underline')
            target.send_keys(' Honest.')
            driver.find_element(By.XPATH, '//button[.="New comment"]').click()
            last_comment_e = driver.find_element(By.XPATH, '//div[@id="comments"]/ul/li[last()]/span')
            self.assertEqual(EXPECTED_COMMENT_HTML, last_comment_e.get_attribute('outerHTML'))

    # Test 6
    def test_several_comments_creation(self):
        NEW_COMMENTS = (
            'Comment from Arseniy №1',
            'Comment from Arseniy №2',
        )

        display_name, email, password = self.TEST_USERS[0]

        driver = webdriver.Chrome()
        with driver:
            driver.get(self.START_URL)
            self._log_in(driver, email, password)

            # Test 6.a
            for comment in NEW_COMMENTS:
                self._post_comment(driver, comment)

            # Test 6.b
            comments = self._get_all_comments(driver)
            for comment, extracted_comment in zip(NEW_COMMENTS, comments[-len(NEW_COMMENTS):]):
                self.assertEqual((comment, display_name), extracted_comment)

    def test_comment_removal(self):
        NEW_COMMENTS = (
            'This comment will be removed',
            'New comment',
        )

        driver = webdriver.Chrome()
        with driver:
            driver.get(self.START_URL)
            self._log_in_test_user(driver)

            for comment in NEW_COMMENTS:
                self._post_comment(driver, comment)

            old_comments = self._get_all_comments(driver)
            comment_to_remove = -2
            elems = driver.find_elements(By.XPATH, '//div[@id="comments"]/ul/li')
            elems[comment_to_remove].find_element(By.TAG_NAME, 'button').click()
            updated_comments = self._get_all_comments(driver)
            del old_comments[comment_to_remove]
            self.assertEqual(old_comments, updated_comments)

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
            self._post_comment(driver1, "Comment from Arseniy №1")

            with self.open_driver() as driver2:
                # Test 8.b
                driver2.get(self.START_URL)
                self._log_in(driver2, "bob_2001@gmail.com", "bbb")
                self._post_comment(driver2, "Comment from Arseniy №2")
                self.assertEqual(self._get_all_comments(driver2)[-2:],
                                 [("Comment from Arseniy №1", 'Alice A.'),
                                  ("Comment from Arseniy №2", 'Bob B.')],
                                 "Comments are wrong")

                # Test 8.c
                self._post_comment(driver1, "Comment from Arseniy №3")
                self.assertEqual(self._get_all_comments(driver1)[-3:],
                                 [("Comment from Arseniy №1", 'Alice A.'),
                                  ("Comment from Arseniy №2", 'Bob B.'),
                                  ("Comment from Arseniy №3", 'Alice A.')],
                                 "Comments are wrong")

                # Test 8.d
                self.remove_comment(driver2, -1)
                self.assertEqual(self._get_all_comments(driver2)[-2:],
                                 [("Comment from Arseniy №1", 'Alice A.'),
                                  ("Comment from Arseniy №3", 'Alice A.')],
                                 "Comments are wrong")

        # Test 8.e
        with self.open_driver() as driver:
            driver.get(self.START_URL)
            self.assertEqual(self._get_all_comments(driver)[-2:],
                             [("Comment from Arseniy №1", 'Alice A.'),
                              ("Comment from Arseniy №3", 'Alice A.')],
                             "Comments are wrong")


if __name__ == '__main__':
    unittest.main()
