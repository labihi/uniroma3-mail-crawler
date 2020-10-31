import json
import os
import re

import requests
from bs4 import BeautifulSoup

from backend.log import logger
from backend.login import TEMP, get_logged_session

from typing import List, Tuple, Dict

CACHE = f"{TEMP}cache.json"
OUTPUT_FILE = "output.csv"



def find_mails(department, session: requests.Session = None) -> Dict[str, Tuple[str,str]]:
    departmentUrl = f"https://{department}.el.uniroma3.it/"
    if("://" in department):
        departmentUrl = department

    output = dict()

    if session is None:
        session = get_logged_session(departmentUrl)

    cache = {}
    if os.path.isfile(CACHE):
        cache = json.load(open(CACHE, 'r'))
        logger.warning("CACHE in use!")
    else:
        logger.warning("CACHE not found.")

    logger.info("visiting the homepage")
    soup = BeautifulSoup(session.get(departmentUrl).text, 'html.parser')

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
    user_ids = set(map(lambda href: re.search(r'id=([0-9]*)', href).group(1), user_links))

    users_len = len(user_ids)

    # looping through users links
    for index, uid in enumerate(user_ids):
        if uid in cache:
            logger.info(f"CACHE HIT: user {index + 1}/{users_len} ({uid})")
            logger.debug(cache[uid])
            output[uid] = cache[uid]
        else:
            logger.info(f"Visiting user {index + 1}/{users_len} ({uid})")
            # visiting the page
            link = f"{departmentUrl}user/profile.php?id={uid}"
            soup = BeautifulSoup(session.get(link).text, 'html.parser')
            # finding the mail
            mail = soup.select_one('.profile_tree a[href*="mailto"]')
            if mail is None:
                logger.warning(f"User {uid} has no mail (look: {link} )")
                continue
            mail = mail.text
            # printing the new ones to console
            logger.debug(mail)
            # adding them to the output
            output[uid] = (mail, soup.select_one("h1").text)

    cache.update(output)
    json.dump(cache, open(CACHE, 'w'))
    logger.warning("CACHE updated")

    # filtering duplicates before returning
    return output


def write_mail_to_file(department):
    # finding mails
    mail_names = find_mails(department)

    # writing to file
    with open(OUTPUT_FILE, 'wb+') as fout:
        fout.write("ID;Nome;Email\n".encode('utf8'))
        for uid in mail_names:
            print(uid)
            mail, name = mail_names[uid]
            if "@stud." in mail:
                test = f"{uid};{mail};{name}\n"
                fout.write(test.encode('utf8'))

    logger.info(f"All data written to: {OUTPUT_FILE}")