import uuid
from .user import User

class Request:
    def __init__(self, content: str, user: User) -> None:
        if not user:
            raise ValueError("Utilisateur requis: vous n'êtes pas authentifié.")
        self._user = user
        if not content:
            raise ValueError("Une requête ne peut pas être vide.")
        self._content = content

        self.requestId = str(uuid.uuid4())

    @property
    def content(self) -> str:
        return self._content
    
    @property
    def user(self) -> User:
        return self._user
    
    @content.setter
    def content(self, c: str) -> None:
        if not c:
            raise ValueError("Une requête ne peut pas être vide.")
        self._content = c
