class Permission:
    def __init__(self, permission_id: int, name: str, description: str = ""):
        self.permission_id = permission_id
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return f"Permission(id={self.permission_id}, name={self.name}, description={self.description})"

    def is_equivalent_to(self, other: "Permission") -> bool:
        return self.name == other.name
