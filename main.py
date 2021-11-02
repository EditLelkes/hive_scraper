from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from bs4 import BeautifulSoup
import re
from player import HivePlayer
import csv
import os

# Fill in boardgame arena login data
USERNAME = os.environ.get('boardgame_arena_username')
PW = os.environ.get('boardgame_arena_password')


# Selenium driver initialization
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)

# Login
driver.get('https://cs.boardgamearena.com/account?redirect=startwannaplay')
sleep(0.5)
username_login = driver.find_element(By.ID, 'username_input').send_keys(USERNAME)
password_login = driver.find_element(By.ID, 'password_input').send_keys(PW)
button_login = driver.find_element(By.ID, 'submit_login_button')
button_login.click()
sleep(2)


# Select all time ranking
driver.get('https://boardgamearena.com/gamepanel?game=hive')
menu = driver.find_element(By.ID, "ranking_menu_menu_title")
menu.click()
alltime = driver.find_element(By.ID, "rankdisplay_all")
alltime.click()

# Clicking 'see more' button to get more players (with every click 10 new players)
seemore = driver.find_element(By.ID, "seemore")
for i in range(3):
    seemore.click()
    sleep(0.2)

# Get html
hive_page = driver.find_element(By.XPATH, "//html").get_attribute('outerHTML')
soup = BeautifulSoup(hive_page, 'html.parser')

# Get players info
players = soup.find_all(
    class_='player_in_list player_in_list_withbaseline player_in_list_fullwidth player_in_list_rank')

hive_players = []

for player in players[10:]:
    player_name = player.find(class_='playername')
    player_href = f'https://boardgamearena.com{player_name["href"]}'
    print(player_href)
    player_elo = player.find(class_='gamerank_value')

    # Get info from profile page
    driver.get(player_href)
    sleep(0.5)
    player_page = driver.find_element(By.XPATH, "//html").get_attribute('outerHTML')
    player_soup = BeautifulSoup(player_page, 'html.parser')

    player_info = player_soup.find(id='pagesection_publicinfos')
    values = player_info.find_all(class_='row-value')
    player_values = [a.text.strip() for a in values]
    player_age = player_values[0].split(' ')[0]
    player_languages = player_values[1].split(',')
    player_country = player_values[2].split(',')[0]

    # Get gaming stats for hive
    prestige = driver.find_element(By.ID, "pageheader_prestige")
    prestige.click()
    sleep(0.2)
    prestige_page = driver.find_element(By.XPATH, "//html").get_attribute('outerHTML')
    prestige_soup = BeautifulSoup(player_page, 'html.parser')
    hive_all = prestige_soup.find_all('a', string='Hive')
    for hive_a in hive_all:
        hive_div = hive_a.parent
        hive_parameters = hive_div.find(class_='palmares_details')
        if hive_parameters is not None:
            hive_params_nowhitespace = re.sub(r"[\n\t\s]*", "", hive_parameters.text)
            player_params = hive_params_nowhitespace.split('•')
            player_games = re.findall(r'\d+', player_params[0])[0]
            player_wins = re.findall(r'\d+', player_params[1])[0]

    # Create hive_player
    hive_player = HivePlayer(player_name.text, player_href, player_age, player_country, player_languages,
                             int(player_elo.text), int(player_games), int(player_wins))

    # Add hive player to list of hive players
    hive_players.append(hive_player)


# Create csv from hive players data
with open('hive_players.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    writer.writerow(['Name', 'Href', 'Age', 'Country', 'Languages', 'ELO', 'Games Played', 'Game Wins'])

    for p in hive_players:
        writer.writerow([p.name, p.href, p.age, p.country, p.languages, p.elo, p.nr_games, p.nr_wins])










