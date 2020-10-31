import sys
from typing import Dict

import edgedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

import os
import pickle

import requests
from bs4 import BeautifulSoup

from backend.log import logger

import chromedriver_autoinstaller

TEMP = 'temp/'
if not os.path.isdir(TEMP):
    os.mkdir(TEMP)

SESSION_FILE = f"{TEMP}d3p4r7m3n7_session.pk"


def _import_cookies(session, cookies: Dict[str, str]):
    for cookie in cookies:
        if 'httpOnly' in cookie:
            cookie['rest'] = {'httpOnly': cookie.pop('httpOnly')}
        if 'expiry' in cookie:
            cookie['expires'] = cookie.pop('expiry')
        if 'sameSite' in cookie:
            cookie.pop('sameSite')
        session.cookies.set(**cookie)

    # pickle.dump(session)


def get_logged_session(department):
    session_file = SESSION_FILE.replace("d3p4r7m3n7", department)
    session = requests.Session()

    # if there's an already serialized session then i load it
    if os.path.exists(session_file):
        session = pickle.load(open(session_file, 'rb'))
    else:
        logger.info("No session saved, login is required")

    # region automated_login
    logged_in = _is_logged_in(session, department)
    if not logged_in:
        logger.warning("Trying automated login...")
        try:
            cookies = _automated_login(department=department)
            _import_cookies(session, cookies)
        except Exception as ex:
            logger.error("Automated login failed")
            logger.debug(ex)
    # endregion

    # region interactive_login
    logged_in = _is_logged_in(session, department)
    if not logged_in:
        logger.warning("Trying interactive login...")
        try:
            cookies = _interactive_login(department=department)
            _import_cookies(session, cookies)
        except Exception as ex:
            logger.error("Interactive login failed")
            logger.debug(ex)
    # endregion

    if _is_logged_in(session, department):
        logger.warning("Login Status: OK!")
    else:
        logger.error("Couldn't log in in no way, shutting down");
        sys.exit(1)

    pickle.dump(session, open(session_file, 'wb'))
    return session


def _is_logged_in(session, department):
    # checking if this session is logged in
    response = session.get(f"https://{department}.el.uniroma3.it/")
    soup = BeautifulSoup(response.text, 'html.parser')
    login = soup.select(".login")
    return len(login) == 0


def _get_driver():
    driver = None

    # trying with google chrome
    try:
        chromedriver_autoinstaller.install()
        driver = webdriver.Chrome()
    except:
        pass

    # trying with edge
    try:
        edgedriver_autoinstaller.install()
        driver = webdriver.Edge(executable_path="msedgedriver.exe")
    except:
        pass

    # trying with firefox
    try:
        # TODO: firefoxdriver_autoinstaller.install(True);
        driver = webdriver.Firefox(executable_path="msedgedriver.exe")
    except:
        pass

    if (driver):
        driver.implicitly_wait(5)
        return driver
    else:
        raise Exception("Impossible to connect to a browser, download google chrome.")


def _automated_login(driver=None, department="ingegneria"):
    import login_data

    if driver is None:
        driver = _get_driver()

    driver.get(f"https://{department}.el.uniroma3.it/login/index.php")

    # writing mail
    mail = driver.find_element_by_css_selector("input[type=email]")
    mail.clear()
    mail.send_keys(login_data.email)
    mail.send_keys(Keys.RETURN)

    # writing password
    passw = driver.find_element_by_css_selector("input[type=password]")
    passw.clear()
    passw.send_keys(login_data.password)
    passw.send_keys(Keys.RETURN)

    # finding submit button
    current_url = driver.current_url
    _retry(lambda: driver.find_element_by_css_selector("input[type=submit]").click())

    # waiting for the url to change after the login
    WebDriverWait(driver, 15).until(EC.url_changes(current_url))

    # returning the login cookies
    return driver.get_cookies()


def _interactive_login(driver=None, department="ingegneria"):
    if driver is None:
        driver = _get_driver()

    driver.get(f"https://{department}.el.uniroma3.it/login/index.php")
    current_url = driver.current_url

    # waiting for the url to change after the login
    WebDriverWait(driver, 300).until(EC.url_changes(current_url))

    # returning the login cookies
    cookies = driver.get_cookies()
    return cookies


def _retry(function, times=1000):
    repeated = 1
    while repeated <= times:
        try:
            function()
            return repeated
        except Exception as ex:
            repeated += 1

    return False
