from dataclasses import dataclass
import time
from typing import Tuple
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver

OUTPUT_FILE = './world_cup_player_stats.csv'

with open('./match_pages.csv') as f:
    lineup_pages = f.read()
    lineup_pages = [i for i in lineup_pages.split(',\n') if i]


@dataclass
class Player:
    """Takes the following parameters and returns them in an output file."""
    name: str
    id_player: int
    country: str
    game_id: int
    time_in: int = None
    start: bool = False
    time_out: int = None

    def write_to_file(self, path: str = OUTPUT_FILE):
        with open(path, 'a') as player_file:
            player_file.write((
                f'{self.name}, {self.id_player}, {self.country}, '
                f'{self.game_id}, {self.start}, {self.time_in}, '
                f'{self.time_out}\n'))


def get_match_id(site: str) -> int:
    return int(site.split('/')[-2])


def get_html(page: str) -> BeautifulSoup:
    """Takes a string and returns it as a BeautifulSoup object."""

    driver = webdriver.Firefox()
    driver.get(page)
    time.sleep(7)
    sauce = driver.execute_script('return document.documentElement.outerHTML')
    driver.quit()
    soup = BeautifulSoup(sauce, 'html5lib')
    return soup


def get_teams(soup: BeautifulSoup) -> Tuple:
    """Takes a BeautifulSoup object and returns a Tuple."""

    home = soup.find('div', class_ ='fi-players__onpitch--home')
    away = soup.find('div', class_ ='fi-players__onpitch--away')
    return home, away


def get_team_name(team_soup) -> str:
    """Takes a BeautifulSoup object and returns a string."""

    team = team_soup.find('div', class_ ='fi-players__teamname')
    country = team.find('span', class_ ='fi-t__nText')
    return country.text


def player_helper(i, home_team_name, away_team_name, game_id, home=True,
                  start=True):
    player_name, player_id = _player_name_and_id(i)
    time_out = _time_out(i)
    if home:
        team = home_team_name
    else:
        team = away_team_name
    if start:
        time_in = 0
    else:
        time_in = _time_in(i)
    player = Player(name=player_name, id_player=player_id, game_id=game_id,
                    country=team, start=start, time_in=time_in,
                    time_out=time_out)
    player.write_to_file()


def _time_in(list_item) -> str:
    """Takes a list item and returns an int."""
    time_in = list_item.find(
        'span', class_ ='fi-p__event fi-p__event--substitution-in')
    if time_in:
        time_in = time_in['title'].replace("'", '')
    return time_in


def _time_out(list_item, start: bool = False) -> str:
    """Takes a list item and returns an int."""
    time_out = list_item.find(
        'span', class_ = 'fi-p__event fi-p__event--substitution-out')
    if time_out:
        time_out = time_out['title'].replace("'", '')
    return time_out


def _player_name_and_id(list_item) -> Tuple:
    """Takes a list item and returns a Tuple."""
    player_name = list_item.find(
        'div', class_ ='fi-p fi-i--0')['data-player-name']
    player_id = list_item.find(
        'div', class_ ='fi-p fi-i--0')['data-player-id']
    return str(player_name).title(), int(player_id)


def get_player_stats(home_soup, away_soup, game_id, home_team_name,
                     away_team_name) -> None:
    """Takes two BeautifulSoup objects, an int, and two strings and returns them
       as a data frame."""
    base_params = {'home_team_name': home_team_name,
                   'away_team_name': away_team_name,
                   'game_id': game_id}
    home_starters = home_soup.find_all('li', class_='home--p')
    for i in home_starters:
        player_helper(i, home=True, start=True, **base_params)

    home_bench = home_soup.find_all('li', class_='home--s')
    for i in home_bench:
        player_helper(i, home=True, start=False, **base_params)

    away_starters = away_soup.find_all('li', class_='away-p')
    for i in away_starters:
        player_helper(i, home=False, start=True, **base_params)

    away_bench = away_soup.find_all('li', class_='away-s')
    for i in away_bench:
        player_helper(i, home=False, start=False, **base_params)


def main(page):
    game_id = get_match_id(page)
    sauce = get_html(page)
    home_sauce, away_sauce = get_teams(sauce)
    home_team_name = get_team_name(home_sauce)
    away_team_name = get_team_name(away_sauce)
    get_player_stats(home_soup=home_sauce, away_soup=away_sauce,
                     game_id=game_id, home_team_name=home_team_name,
                     away_team_name=away_team_name)
    time.sleep(5)


if __name__ == '__main__':
    to_retry = List = []
    print('Getting player stats from match: ')
    for page in tqdm(lineup_pages):
        main(page)
#           except Exception:
#           to_retry.append(page)
#    if to_retry:
#        print(f'Attempt 2, there are {len(to_retry)} to try to scrape again.')
#        for page in tqdm(to_retry):
#            try:
#                main()
#            except Exception:
#                print(page)
