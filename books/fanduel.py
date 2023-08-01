import hashlib
from datetime import datetime
from schema import BookResponse, Market, Outcome
from utils import APIException, to_dict
from fuzzy import parse_name
import requests

class FanduelAPI:
    """
    Interface with hidden Fanduel API
    """
    def __init__(self):
        self.api_key = "FhMFpcPWXMeyZxOx"
        self.base_url = "https://sbapi.ny.sportsbook.fanduel.com/api"
        self.timezone = "America/New_York"
        self.provider = "Fanduel"

        self.sport = None
        self.sport_code = None

        self.sport_keys = {
            "baseball_mlb": "mlb"
        }
        self.line_keys = {
            "h2h": "Moneyline",
            "spreads": "Total Runs"
        }
    
    def resolve_sport(self,sport):
        """
        Resolve Fanduel sport code from standardized code
        """
        return self.sport_keys[sport]
    
    def parse(self, events: list[dict], markets: list)-> BookResponse:
        """
        Parse json from Fanduel API
        """
        parsed_events: list[BookResponse] = []
        events = events.values()
        markets = markets.values()
        for event in events:            

            parsed_away = ""
            parsed_home = ""
            event_markets = []
            for line in markets:
                if line["marketName"] == "Moneyline" and line["eventId"] == event["eventId"]:

                    away_team = line["runners"][0]
                    home_team = line["runners"][1]
                    parsed_away = parse_name(self.sport, away_team["runnerName"])
                    parsed_home = parse_name(self.sport, home_team["runnerName"])
                    outcomes_money: list[Outcome] = [
                        Outcome(
                            name=parsed_away,
                            price=away_team["winRunnerOdds"]["trueOdds"]["decimalOdds"]["decimalOdds"]
                        ),
                        Outcome(
                            name=parsed_home,
                            price=home_team["winRunnerOdds"]["trueOdds"]["decimalOdds"]["decimalOdds"]
                        )
                    ]
                    money_market_data = Market(
                        key="h2h",
                        outcomes=outcomes_money
                    )
                    event_markets.append(money_market_data)
                elif line["marketType"] == "TOTAL_POINTS_(OVER/UNDER)" and line["eventId"] == event["eventId"]:
                    outcomes_spread: list[Outcome] = [
                        Outcome(
                            name="Over",
                            price=line["runners"][0]["winRunnerOdds"]["trueOdds"]["decimalOdds"]["decimalOdds"],
                            point=line["runners"][0]["handicap"]
                        ),
                        Outcome(
                            name="Under",
                            price=line["runners"][1]["winRunnerOdds"]["trueOdds"]["decimalOdds"]["decimalOdds"],
                            point= -line["runners"][1]["handicap"]
                        )
                    ]
                    spread_market_data = Market(
                        key="spreads",
                        outcomes=outcomes_spread
                    )
                    event_markets.append(spread_market_data)
                event_string = f'{parsed_away}-{parsed_home}-{event["openDate"][:10]}'
                event_hash = hashlib.md5(bytes(event_string, encoding='utf-8')).hexdigest()

                parsed_events.append(to_dict(
                    BookResponse(
                        key=self.provider,
                        title=event["name"],
                        event_hash=event_hash,
                        last_update=datetime.now(),
                        markets=event_markets
                    ))
                ) 
        return parsed_events
                

    def fetch(self, sport) -> BookResponse:
        """
        Fetch and transform data from Fanduel
        """
        sport_code = self.resolve_sport(sport)
        self.sport = sport
        self.sport_code = sport_code

        resp = requests.get(f'{self.base_url}/content-managed-page?page=CUSTOM&customPageId={sport_code}&_ak={self.api_key}&timezone={self.timezone}', timeout=10)

        if not resp.ok:
            raise APIException(self.provider, "Error fetching API")
        
        data = resp.json()["attachments"]

        events = data["events"]
        markets = data["markets"]
        finished_data = self.parse(events, markets)
        return finished_data