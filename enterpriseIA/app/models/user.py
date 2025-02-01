from abc import ABC, abstractmethod



class User(ABC):
    def __init__(self, user_id: int, username: str, hashed_password: str, fullname: str = "")->None:
        self.user_id = user_id
        self.username = username
        self.hashed_password = hashed_password
        self.fullname = fullname

    @abstractmethod
    def isauthenticate(self) -> bool:
        pass

    @abstractmethod
    def authenticate(self) -> bool:
        pass
    def getUsername(self)-> str:
        return self.username + ": " + self.fullname
    