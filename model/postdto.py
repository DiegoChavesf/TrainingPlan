#PostDto
from datetime import datetime

class PostDto:
    def __init__(self, content, activity_id, user_id):
        self._content = content
        self._activity_id = activity_id
        self._user_id = user_id
        self._date = datetime.now()