from datetime import datetime

class Outcome:

    def __init__(
        self,
        name: str,
        price: float,
        point: float|None=None
    ):
        self.name = name
        self.price = price
        self.point = point
    

class Market:

    def __init__(
        self,
        key: str,
        outcomes: list[Outcome]
    ):
        self.key = key
        self.outcomes = outcomes

class BookResponse:
    
    def __init__(
        self,
        key: str,
        title: str,
        event_hash: str,
        last_update: datetime,
        markets: list[Market]
    ):
        self.key = key
        self.title = title
        self.event_hash = event_hash
        self.last_update = last_update
        self.markets = markets
    