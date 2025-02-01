from .user import User

class Employee(User):
    def __init__(self, user_id: int, username: str, hashed_password: str, fullname: str = "", department: str = ""):
        super().__init__(user_id, username, hashed_password, fullname)
        self.department = department

    def isauthenticate(self) -> bool:
        return self.user_id is not None

    def authenticate(self) -> bool:
        return self.isauthenticate()
