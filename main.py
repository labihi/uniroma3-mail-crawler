import requests
from bs4 import BeautifulSoup

from login import get_logged_session


def crawl(department, session: requests.Session = None):
    if(session is None):
        session = get_logged_session(department)

    response = session.get(f"https://{department}.el.uniroma3.it/")
    soup = BeautifulSoup(response.text, 'html.parser')
    print(response.text)


if __name__ == '__main__':
    crawl("ingegneria")
