import hashlib
from databaseHandler import (
    create_user,
    get_user_by_username,
    create_role,
    get_role_by_name,
    create_permission,
    get_permission_by_name,
    assign_role_to_user,
    assign_permission_to_role,   
    get_roles_for_user,
    insert_request,
    insert_response,
    insert_audit_log,
    get_all_audit_logs,
    get_all_permissions  
)
from .modules.filter_module import FilterModule
from .modules.access_control import AccessControl
from .modules.audit_module import AuditModule
from .models.employee import Employee
from .models.admin import Admin
from .models.dpo import DPO
from .models.request import Request
from .models.response import Response
from .models.local_ia_service import LocalIAService
from .models.external_ia_service import ExternalIAService
from .modules.compliance_module import ComplianceModule

class System:
    def __init__(self, external_api_key: str = "", retention_days: int = 90):
        self.filter_module = FilterModule()
        self.access_control = AccessControl()
        self.audit_module = AuditModule()
        self.localAI = LocalIAService()
        self.externalAI = ExternalIAService(api_key=external_api_key)
        self.compliance_module = ComplianceModule(retention_days=retention_days)
        self.compliance_module.enforce_data_retention()

    # --------------------------------------------------------------------------
    # USER CREATION & AUTHENTICATION
    # --------------------------------------------------------------------------
    def createUser(self, username: str, password: str, fullname: str = "", department: str = "", role_names=None):
        if role_names is None:
            role_names = ["EMPLOYEE"]
        hashed_pw = hashlib.sha256(password.encode("utf-8")).hexdigest()
        user_id = create_user(username, hashed_pw, fullname, department)
        for rn in role_names:
            existing_role = get_role_by_name(rn)
            if not existing_role:
                create_role(rn, f"Auto-created role {rn}")
                existing_role = get_role_by_name(rn)
            assign_role_to_user(user_id, existing_role[0])
        return user_id

    def ensure_use_ia_permission_exists():
        existing_perm = get_permission_by_name("USE_IA")
        if not existing_perm:
            create_permission("USE_IA", "Permission to use internal AI")

    def authenticateUser(self, username: str, password: str):
        user_tuple = get_user_by_username(username)
        if not user_tuple:
            return None
        user_id = user_tuple[0]
        user_name = user_tuple[1]
        hashed_pw = user_tuple[2]
        full_name = user_tuple[3]
        department = user_tuple[4]
        input_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if input_hash != hashed_pw:
            return None
        roles_data = get_roles_for_user(user_id)
        role_names = [r[1] for r in roles_data]
        if "ADMIN" in role_names:
            return Admin(user_id=user_id, username=user_name, hashed_password=hashed_pw, fullname=full_name)
        elif "DPO" in role_names:
            return DPO(user_id=user_id, username=user_name, hashed_password=hashed_pw, fullname=full_name)
        else:
            return Employee(user_id=user_id, username=user_name, hashed_password=hashed_pw, fullname=full_name, department=department)

    # --------------------------------------------------------------------------
    # ROLE AND PERMISSION MANAGEMENT
    # --------------------------------------------------------------------------
    def createRole(self, user, role_name: str, description: str = ""):
        if not self._canManageRoles(user):
            return "Permission denied: user cannot manage roles."
        role_id = create_role(role_name, description)
        insert_audit_log(user.user_id, "CREATE_ROLE", f"Created role '{role_name}' with ID {role_id}")
        return f"Role '{role_name}' created with ID {role_id}."

    def updateRoleDescription(self, user, role_id: int, new_description: str):
        if not self._canManageRoles(user):
            return "Permission denied: user cannot manage roles."
        from databaseHandler import update_role_description
        update_role_description(role_id, new_description)
        insert_audit_log(user.user_id, "UPDATE_ROLE", f"Updated role {role_id} with description: {new_description}")
        return f"Role {role_id} updated with new description."

    def deleteRole(self, user, role_id: int):
        if not self._canManageRoles(user):
            return "Permission denied: user cannot manage roles."
        from databaseHandler import delete_role
        delete_role(role_id)
        insert_audit_log(user.user_id, "DELETE_ROLE", f"Deleted role {role_id}")
        return f"Role {role_id} deleted."

    def createPermission(self, user, permission_name: str, description: str = ""):
        if not self._canManageRoles(user):
            return "Permission denied: user cannot manage roles/permissions."
        perm_id = create_permission(permission_name, description)
        insert_audit_log(user.user_id, "CREATE_PERMISSION", f"Created permission '{permission_name}' (ID {perm_id})")
        return f"Permission '{permission_name}' created with ID {perm_id}."
    
    def getAllPermissions(self):
        """
        Wrapper method to retrieve all permissions using the database handler.
        Returns:
            A list of permission dictionaries.
        """
        return get_all_permissions()

    def updatePermissionDescription(self, user, permission_id: int, new_description: str):
        if not self._canManageRoles(user):
            return "Permission denied: user cannot manage roles/permissions."
        from databaseHandler import update_permission_description
        update_permission_description(permission_id, new_description)
        insert_audit_log(user.user_id, "UPDATE_PERMISSION", f"Updated permission {permission_id} with description: {new_description}")
        return f"Permission {permission_id} updated with new description."

    def deletePermission(self, user, permission_id: int):
        if not self._canManageRoles(user):
            return "Permission denied: user cannot manage roles/permissions."
        from databaseHandler import delete_permission
        delete_permission(permission_id)
        insert_audit_log(user.user_id, "DELETE_PERMISSION", f"Deleted permission {permission_id}")
        return f"Permission {permission_id} deleted."

    def attachPermissionToRole(self, user, role_id: int, permission_id: int):
        if not self._canManageRoles(user):
            return "Permission denied: user cannot manage roles/permissions."
        assign_permission_to_role(role_id, permission_id)
        insert_audit_log(user.user_id, "ATTACH_PERMISSION_TO_ROLE", f"Attached permission {permission_id} to role {role_id}")
        return f"Permission {permission_id} attached to role {role_id}."

    def detachPermissionFromRole(self, user, role_id: int, permission_id: int):
        if not self._canManageRoles(user):
            return "Permission denied: user cannot manage roles/permissions."
        from databaseHandler import remove_permission_from_role
        remove_permission_from_role(role_id, permission_id)
        insert_audit_log(user.user_id, "DETACH_PERMISSION_FROM_ROLE", f"Removed permission {permission_id} from role {role_id}")
        return f"Permission {permission_id} removed from role {role_id}."

    def _canManageRoles(self, user):
        if not user or not user.isauthenticate():
            return False
        return self.access_control.user_has_permission(user, "CONFIGURE_SYSTEM")

    # --------------------------------------------------------------------------
    # EMPLOYEE MAKES A REQUEST
    # --------------------------------------------------------------------------
    def makeRequest(self, user, content: str, use_external_ai: bool = False):
        if not user or not user.isauthenticate():
            return Response("User is not authenticated.", None)
        req = Request(content=content, user=user)
        insert_request(req.requestId, user.user_id, req.content)
        if not self.compliance_module.has_valid_consent(user.user_id):
            denied_response = Response("No consent for AI processing.", req)
            insert_response(req.requestId, denied_response.content)
            self.audit_module.log_request(req)
            self.audit_module.log_response(denied_response)
            return denied_response
        if use_external_ai:
            self.filter_module.run_detection_and_anonymization(req)
            if not self.access_control.user_has_permission(user, "AI_USE_EXTERNAL"):
                msg = "Permission denied: user cannot use external AI."
                denied_response = Response(msg, req)
                self.audit_module.log_request(req)
                self.audit_module.log_response(denied_response)
                return denied_response
            response = self.externalAI.processRequest(req)
        else:
            if not self.access_control.user_has_permission(user, "USE_IA"):
                msg = "Permission denied: user cannot use local AI."
                denied_response = Response(msg, req)
                self.audit_module.log_request(req)
                self.audit_module.log_response(denied_response)
                return denied_response
            response = self.localAI.processRequest(req)
        insert_response(req.requestId, response.content)
        self.audit_module.log_request(req)
        self.audit_module.log_response(response)
        return response

    def eraseUserData(self, acting_user, target_user_id: int):
        if not self.access_control.user_has_permission(acting_user, "MANAGE_COMPLIANCE"):
            return "Permission denied: cannot erase user data."
        self.compliance_module.erase_user_data(target_user_id, acting_user.user_id)
        return f"Data for user {target_user_id} has been erased."

    def setUserConsent(self, acting_user, target_user_id: int, consent: bool):
        if acting_user.user_id != target_user_id:
            if not self.access_control.user_has_permission(acting_user, "MANAGE_COMPLIANCE"):
                return "Permission denied: cannot change another user's consent."
        from databaseHandler import set_user_consent
        set_user_consent(target_user_id, consent)
        insert_audit_log(acting_user.user_id, "SET_CONSENT", f"User {acting_user.user_id} set consent={consent} for user {target_user_id}")
        return f"Consent set to {consent} for user {target_user_id}."

    def enforceRetentionNow(self, acting_user):
        if not self.access_control.user_has_permission(acting_user, "MANAGE_COMPLIANCE"):
            return "Permission denied: cannot enforce retention."
        self.compliance_module.enforce_data_retention()
        insert_audit_log(acting_user.user_id, "RETENTION_ENFORCED", "Manually enforced data retention.")
        return "Retention policy applied successfully."

    # --------------------------------------------------------------------------
    # ADMIN HANDLES MODELS
    # --------------------------------------------------------------------------
    def adminLoadLocalModel(self, user, model_name: str):
        if not user or not user.isauthenticate():
            return "Not authenticated."
        if not self.access_control.user_has_permission(user, "CONFIGURE_SYSTEM"):
            return "Permission denied: user cannot configure system."
        if self.localAI.loadModel(model_name):
            return f"Model '{model_name}' loaded successfully."
        return f"Failed to load model '{model_name}'."

    def adminSetExternalAPIKey(self, user, new_api_key: str):
        if not user or not user.isauthenticate():
            return "Not authenticated."
        if not self.access_control.user_has_permission(user, "CONFIGURE_SYSTEM"):
            return "Permission denied: user cannot configure system."
        self.externalAI.api_key = new_api_key
        return "External API key updated successfully."

    # --------------------------------------------------------------------------
    # AUDITOR VIEWS LOGS
    # --------------------------------------------------------------------------
    def getAllAuditLogs(self, user):
        if not user or not user.isauthenticate():
            return []
        if not self.access_control.user_has_permission(user, "VIEW_LOGS"):
            return ["Permission denied: user cannot view logs."]
        return get_all_audit_logs()
