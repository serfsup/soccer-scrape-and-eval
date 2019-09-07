import requests
import time
import os
from typing import Tuple, Set
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_SITE = 'https://www.fifa.com/worldcup/matches/'
EXTENSIONS = ('groupphase', 'knockoutphase')
SPECIFIER = '#match-lineups'


def create_match_pages(base: str, suffixes: Tuple) -> Set:
    """
    Takes a base webpage and adds extensions onto it.
    Returns a set of websites to extract data from.
    """
    match_pages = set()
    for suffix in suffixes:
        match_pages.add(f'{base}#{suffix}')
    return match_pages


def get_match_number(sites: Set) -> Set[str]:
    """
    Takes a set of sites and returns a set which contains the unique match
    numbers.
    """
    print('gettings match_ids', '\n')
    match_ids = set()
    for site in tqdm(sites):
        sauce = requests.get(site, timeout=20)
        soup = BeautifulSoup(sauce.content, 'html5lib')
        ids = soup.find_all('div', class_='fi-mu result fi-mu-national result')
        for i in ids:
            match_ids.add(str(i['data-id']))
        time.sleep(5)
    return match_ids


def create_lineup_links(base: str, spec_add: str, match_ids: Set) -> Set[str]:
    """Takes a set of match ids and creates links to the match lineups."""
    return (f'{base}match/{i}/{spec_add}' for i in match_ids)


if __name__ == '__main__':
    pages = create_match_pages(BASE_SITE, EXTENSIONS)
    match_ids = get_match_number(pages)
    lineup_links = create_lineup_links(BASE_SITE, SPECIFIER, match_ids)
    os.chdir('/Users/danmchenry/Desktop/soccer_scrape')
    with open('match_pages.csv', 'a') as match:
        for i in lineup_links:
            match.write(f'{i},\n')
