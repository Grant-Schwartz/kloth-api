from schema import BookResponse, Market, Outcome
from utils import APIException, to_dict
from fuzzy import parse_name
import requests
import hashlib
from datetime import datetime
import json

class DraftKingsAPI:

    def __init__(self):
        self.base_url = "https://sportsbook-us-pa.draftkings.com/sites/US-PA-SB/api/v5"
        self.provider = "DraftKings"
    
        self.sport_keys = {
            "baseball_mlb": "84240"
        }

    def resolve_sport(self,sport):
        """
        Resolve DraftKings sport code from standardized code
        """
        return self.sport_keys[sport]
    
    def parse(self, events: list[dict], markets: list)-> BookResponse:
        parsed_events: list[BookResponse] = []
        for event in events:
            parsed_away = parse_name(self.sport, event["teamName1"])
            parsed_home = parse_name(self.sport, event["teamName2"])

            for line in markets:
                if line[0]["eventId"] == event["eventId"]:
                    outcomes = []
                    if "label" in line[-1].keys():
                        outcomes_money: list[Outcome] = [
                            Outcome(
                                name=parsed_away,
                                price=line[-1]["outcomes"][0]["oddsDecimal"]
                            ),
                            Outcome(
                                name=parsed_home,
                                price=line[-1]["outcomes"][1]["oddsDecimal"]
                            )
                        ]
                        moneyline = Market(
                            key="h2h",
                            outcomes=outcomes_money
                        )
                        outcomes.append(moneyline)
                    if "label" in line[1].keys():
                        outcomes_spread: list[Outcome] = [
                            Outcome(
                                name="Over",
                                price=line[1]["outcomes"][0]["oddsDecimal"],
                                point=line[1]["outcomes"][0]["line"]
                            ),
                            Outcome(
                                name="Under",
                                price=line[1]["outcomes"][1]["oddsDecimal"],
                                point=line[1]["outcomes"][1]["line"]
                            )
                        ]
                        spreads = Market(
                            key="spreads",
                            outcomes=outcomes_spread
                        )
                        outcomes.append(spreads)
                    break

            
            event_string = f'{parsed_home}-{parsed_away}-{event["startDate"][:10]}'
            event_hash = hashlib.md5(bytes(event_string, encoding='utf-8')).hexdigest()

            parsed_events.append(to_dict(
                BookResponse(
                    key=self.provider,
                    title=event["name"],
                    event_hash=event_hash,
                    last_update=datetime.now(),
                    markets=outcomes
                ))
            ) 
        return parsed_events
                
            
    
    def fetch(self, sport) -> BookResponse:
        """
        Fetch from DraftKings API and return BookResponse type
        """
        sport_code = self.resolve_sport(sport)
        self.sport = sport
        self.sport_code = sport_code

        resp = requests.get(f'{self.base_url}/eventgroups/{self.sport_code}?format=json')

        if not resp.ok:
            raise APIException(self.provider, "Error fetching API")
        
        data = resp.json()

        events = data["eventGroup"]["events"]
        markets = data["eventGroup"]["offerCategories"][0]["offerSubcategoryDescriptors"][0]["offerSubcategory"]["offers"]

        finished_data = self.parse(events, markets)
        return  finished_data

test = DraftKingsAPI()
test.fetch("baseball_mlb")
