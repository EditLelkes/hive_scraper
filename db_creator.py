import re
import os
from datetime import datetime
from time import sleep
from typing import List
import csv
import xlsxwriter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from player import HivePlayer


class DatabaseCreator:

    def __init__(self, player_list: List[HivePlayer]):
        self.player_list = player_list

    @classmethod
    def create_from_web(cls):
        # Fill in boardgame arena login data
        username = os.environ.get('boardgame_arena_username')
        pw = os.environ.get('boardgame_arena_password')

        # Selenium driver initialization
        s = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=s)

        # Login to boardgame arena
        driver.get('https://cs.boardgamearena.com/account?redirect=startwannaplay')
        sleep(0.5)
        driver.find_element(By.ID, 'username_input').send_keys(username)
        driver.find_element(By.ID, 'password_input').send_keys(pw)
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
        for i in range(1):
            seemore.click()
            sleep(0.2)

        # Get html
        hive_page = driver.find_element(By.XPATH, "//html").get_attribute('outerHTML')
        soup = BeautifulSoup(hive_page, 'html.parser')

        # Get players info
        players = soup.find_all(
            class_='player_in_list player_in_list_withbaseline player_in_list_fullwidth player_in_list_rank')
        print(len(players))

        hive_players = []

        for player in players[10:]:
            player_name = player.find(class_='playername')
            player_href = f'https://boardgamearena.com{player_name["href"]}'
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

            # Get gaming stats for hive -- maybe not needed this part. Hive statistics already on profile page
            # prestige = driver.find_element(By.ID, "pageheader_prestige")
            # prestige.click()
            # sleep(0.2)
            # prestige_page = driver.find_element(By.XPATH, "//html").get_attribute('outerHTML')
            # prestige_soup = BeautifulSoup(player_page, 'html.parser')
            hive_all = player_soup.find_all('a', string='Hive')
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
        return DatabaseCreator(hive_players)

    @classmethod
    def create_from_csv(cls, csv_file) -> "DatabaseCreator":
        # return DatabaseCreator(player_list)
        pass

    def to_csv(self):
        with open('hive_players.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Href', 'Age', 'Country', 'Languages', 'ELO', 'Games Played', 'Game Wins'])
            for player in self.player_list:
                writer.writerow([player.name, player.href, player.age, player.country, player.languages,
                                 player.elo, player.nr_games, player.nr_wins])

    def to_excel(self):
        workbook = xlsxwriter.Workbook(f'{datetime.today().strftime("HIVE_%Y%b%d")}')
        worksheet = workbook.add_worksheet('player_data')
        header = ['Name', 'Age', 'Country', 'Languages', 'ELO', 'Games Played', 'Game Wins']
        header_format = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'black'})

        for col_num, col_name in enumerate(header):
            worksheet.write(0, col_num, col_name, header_format)

        row_num = 1
        for player in self.player_list:
            worksheet.write_url(row_num, header.index('Name'), player.href, string=player.name)
            worksheet.write_string(row_num, header.index('Age'), player.age)
            worksheet.write_string(row_num, header.index('Country'), player.country)
            worksheet.write_string(row_num, header.index('Languages'), ','.join(player.languages))
            worksheet.write_number(row_num, header.index('ELO'), player.elo)
            worksheet.write_number(row_num, header.index('Games Played'), player.nr_games)
            worksheet.write_number(row_num, header.index('Game Wins'), player.nr_wins)
            row_num += 1

        workbook.close()
