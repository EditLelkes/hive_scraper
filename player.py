from typing import List


class HivePlayer:
    def __init__(self, name: str, href: str, age: str, country: str, languages: List[str],
                 elo: int, nr_games: int, nr_wins: int):
        self.name = name
        self.href = href
        self.age = age
        self.country = country
        self.languages = languages
        self.elo = elo
        self.nr_games = nr_games
        self.nr_wins = nr_wins
        self.win_percent = (nr_wins / nr_games) * 100
