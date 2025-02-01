import ollama
from .request import Request
from .response import Response

ollama.pull('mistral')

class LocalIAService:
    def __init__(self):
        pass

    def loadModel(self, nameModel: str) -> bool:
        try:
            ollama.pull(nameModel)
            return True
        except Exception:
            return False

    def processRequest(self, req: Request) -> Response:
        prompt = req.content
        result = ollama.chat(
            model='mistral',
            messages=[{'role': 'user', 'content': prompt}],
        )
        content = result['message']['content']
        return Response(content=content, req=req)

    def processCustomPrompt(self, prompt: str) -> str:
        """
        A direct method that calls the local IA with a single prompt
        and returns the raw string (no Response object).
        Useful for detection or anonymization tasks.
        """
        result = ollama.chat(
            model='mistral',
            messages=[{'role': 'user', 'content': prompt}],
        )
        return result['message']['content']
