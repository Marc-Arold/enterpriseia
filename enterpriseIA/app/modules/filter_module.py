from ..models.request import Request
from ..models.local_ia_service import LocalIAService

class FilterModule:
    """
    Uses local AI to:
      1) Detect sensitive data in the request.
      2) Anonymize the request content if sensitive data is found.
    """
    def __init__(self):
        self.localAI = LocalIAService()

    def detectSensitiveData(self, req: Request) -> bool:
        """
        Calls the local AI with a specialized prompt to detect
        if the content has sensitive data. Returns True/False.
        """
        detection_prompt = (
            "You are a system that detects if the following text contains sensitive data.\n"
            "Respond with 'TRUE' if it contains any sensitive or personal data, or 'FALSE' otherwise.\n\n"
            f"Text:\n{req.content}"
        )

        detection_result = self.localAI.processCustomPrompt(detection_prompt)

        if "TRUE" in detection_result.upper():
            return True
        return False

    def anonymizeData(self, req: Request):
        """
        Calls the local AI with a specialized prompt to anonymize the text,
        removing or masking any sensitive information found.
        """
        anonymize_prompt = (
            "You are a system that removes or masks sensitive data from the text.\n"
            "Return ONLY the anonymized text. Do not include any explanation.\n\n"
            f"Text:\n{req.content}"
        )
        anonymized_text = self.localAI.processCustomPrompt(anonymize_prompt)
        req.content = anonymized_text

    def run_detection_and_anonymization(self, req: Request) -> None:
        """
        Performs the detection of sensitive data,
        and anonymizes if data is found.
        """
        if self.detectSensitiveData(req):
            self.anonymizeData(req)
