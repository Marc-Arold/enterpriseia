from .permissions import Permission
class Role:
    def __init__(self, name: str, description: str= ""):
        self.name = name
        self.description= description
        self.permissions =  set()

    def addPermission(self, p: Permission)-> None:
        self.permissions.add(p)

    def removePermission(self, p:Permission)->None:
        self.permissions.discard(p)
    
    def hasPermission(self, p: Permission) -> bool:
        return p in self.permissions
    
    def __repr__(self) -> str:
        return f"Role(name={self.name}, permissions={[perm.name for perm in self.permissions]})"
