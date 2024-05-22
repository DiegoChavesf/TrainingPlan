# ActivityDto
from datetime import datetime

class ActivityDto:
    def __init__(self, name, description, user_id, kudos):
        self._name = name
        self._description = description
        self._user_id = user_id
        self._kudos = kudos
        self._date = datetime.now()