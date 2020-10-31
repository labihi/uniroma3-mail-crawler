import requests
from bs4 import BeautifulSoup

from login import get_logged_session


def find_mails(department, session: requests.Session = None):
    output = set()

    if session is None:
        session = get_logged_session(department)

    # visiting the homepage
    soup = BeautifulSoup(session.get(f"https://{department}.el.uniroma3.it/").text, 'html.parser')

    # finding the courses links
    courses = soup.select('.list-group a.list-group-item-action[data-parent-key="mycourses"]')
    # mapping them to the partecipants links
    partecipants_links = map(
        lambda course: course['href'].replace('course/view.php', 'user/index.php') + "&perpage=10000", courses)

    # looping through partecipant_links (per course)
    for partecipant_link in partecipants_links:
        # visiting the page
        soup = BeautifulSoup(session.get(partecipant_link).text, 'html.parser')
        # finding the user links and mapping them to the href
        user_links = map(lambda user: user['href'], soup.select('#participants tbody a'))
        # looping through users in this course
        for user_link in user_links:
            # visiting the page
            soup = BeautifulSoup(session.get(user_link).text, 'html.parser')
            # finding all the mails (even tho it should be only one)
            mails = set(map(lambda mail_link: mail_link.text, soup.select('.profile_tree a[href*="mailto"]')))
            # printing the new ones to console
            print(mails.difference(output))
            # adding them to the output
            output.union(mails)

    # filtering duplicates before returning
    return set(output)


if __name__ == '__main__':
    print(find_mails("ingegneria"))
