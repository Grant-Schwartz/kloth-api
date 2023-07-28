from fuzzywuzzy import process

matches = {
    "baseball_mlb": ["Angels", "Astros", "Athletics", "Blue Jays", "Braves", "Brewers", "Cardinals", "Cubs", "Dodgers", "Giants", "Indians", "Mariners", "Marlins", "Mets", "Nationals", "Orioles", "Padres", "Phillies", "Pirates", "Rangers", "Rays", "Red Sox", "Reds", "Rockies", "Royals", "Tigers", "Twins", "White Sox", "Yankees"]
}

def parse_name(sport: str, team: str):
    return process.extractOne(team, matches[sport])[00]
