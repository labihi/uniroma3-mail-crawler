import logging
import re

import requests
from bs4 import BeautifulSoup

from log import logger
from login import get_logged_session


def find_mails(department, session: requests.Session = None):
    output = set()

    if session is None:
        session = get_logged_session(department)

    logger.info("visiting the homepage")
    soup = BeautifulSoup(session.get(f"https://{department}.el.uniroma3.it/").text, 'html.parser')

    # finding the courses links
    courses = soup.select('.list-group a.list-group-item-action[data-parent-key="mycourses"]')
    # mapping them to the partecipants links
    partecipants_links = map(
        lambda course: course['href'].replace('course/view.php', 'user/index.php') + "&perpage=10000", courses)

    user_links = []

    # looping through partecipant_links (per course) to extract the user links
    for partecipant_link in partecipants_links:
        logger.info(f"visiting course partecipants ({partecipant_link})")
        # visiting the page
        soup = BeautifulSoup(session.get(partecipant_link).text, 'html.parser')
        # finding the user links and mapping them to the href
        user_links.extend(map(lambda user: user['href'], soup.select('#participants tbody a')))

    # removing the duplicated user links by mapping them into a regex that pick their code up
    user_ids = set(map(lambda link: re.search(r'id=([0-9]*)', link).group(1), user_links))

    # remapping the ids to their links
    user_links = map(lambda uid: f"https://{department}.el.uniroma3.it/user/profile.php?id={uid}", user_ids)

    users_len = len(user_ids)

    # looping through users links
    for index, user_link in enumerate(user_links):
        logger.info(f"Visiting user {index}/{users_len} ({user_link})")
        # visiting the page
        soup = BeautifulSoup(session.get(user_link).text, 'html.parser')
        # finding all the mails (even tho it should be only one)
        mails = set(map(lambda mail_link: mail_link.text, soup.select('.profile_tree a[href*="mailto"]')))
        # printing the new ones to console
        logger.debug(mails.difference(output))
        # adding them to the output
        output.update(mails)

    # filtering duplicates before returning
    return set(output)


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    logger.info(find_mails("ingegneria"))
