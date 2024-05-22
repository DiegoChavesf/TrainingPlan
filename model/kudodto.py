#KudoDto
from datetime import datetime

class KudoDto:
    def __init__(self, has_liked, activity_id, user_id):
        self._has_liked = has_liked
        self._activity_id = activity_id
        self._user_id = user_id
        self._date = datetime.now()