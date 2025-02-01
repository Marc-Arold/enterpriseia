import uuid
from .request import Request

class Response:
    def __init__(self, content: str, req: Request) -> None:
        if not req:
            raise ValueError("Requête requise: pas de réponse sans requête.")
        self._request = req
        if not content:
            raise ValueError("Une réponse ne peut pas être vide.")
        self._content = content

        self.responseId = str(uuid.uuid4())

    @property
    def content(self) -> str:
        return self._content
    
    @property
    def requete(self) -> Request:
        return self._request
