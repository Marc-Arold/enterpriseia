from databaseHandler import insert_audit_log
from ..models.request import Request
from ..models.response import Response

class AuditModule:
    """
    Logs user actions to the database for auditing.
    """
    def log_request(self, req: Request):
        """
        Logs the request action in the audit_logs table.
        """
        user_id = req.user.user_id
        action = "REQUEST_SUBMITTED"
        details = f"Request ID: {req.requestId}, Content: {req.content}"
        insert_audit_log(user_id, action, details)

    def log_response(self, res: Response):
        """
        Logs the response action in the audit_logs table.
        """
        user_id = res.requete.user.user_id
        action = "RESPONSE_GENERATED"
        details = f"Response ID: {res.responseId}, RequestID: {res.requete.requestId}"
        insert_audit_log(user_id, action, details)
