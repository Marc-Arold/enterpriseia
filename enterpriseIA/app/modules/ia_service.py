from abc import ABC, abstractmethod
from ..models.request import Request

class IAService:
    @abstractmethod
    def processRequest(req:Request)->str:
        pass