import requests  
from ..modules.ia_service import IAService
from .request import Request
from .response import Response
from openai import OpenAI
import json
class ExternalIAService(IAService):
    """
    Example external AI service that calls an API (OpenAI or similar).
    Adjust this to your actual external provider logic.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key

    def processRequest(self, req: Request) -> Response:
        try:
            client = OpenAI(api_key=self.api_key)
            
            # Ajouter une instruction explicite pour le JSON
            json_instruction = "Respond in valid JSON format. "
            prompt = f"{json_instruction}[External AI response to]: {req.content}"
            
            response = client.chat.completions.create(
                model="gpt-4-0125-preview",  # Modèle corrigé
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that responds in JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Validation du JSON
            text = response.choices[0].message.content
            json.loads(text)  # Lève une exception si invalide
            
            return Response(content=text, req=req)
        
        except json.JSONDecodeError:
            return Response(content='{"error": "Invalid JSON response"}', req=req)
        except Exception as e:
            return Response(content=f'{{"error": "API Error: {str(e)}"}}', req=req)
