import hashlib
import os
from environ import Env
from app.gui.login_window import main 
from databaseHandler import (
    create_user, get_user_by_username,get_user_by_id,
    create_role, get_role_by_name,
    create_permission, get_permission_by_name,
    assign_role_to_user, assign_permission_to_role,
    get_roles_for_user, get_permissions_for_role,
    insert_request, insert_response, insert_audit_log
)
from app.models.employee import Employee
from app.models.request import Request
from app.models.response import Response
from app.system import System
import logging
import sqlite3

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'my_database.sqlite')
    logging.info(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    db_path = os.path.join(os.path.dirname(__file__), 'my_database.sqlite')
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        logging.info("Existing database removed. Creating fresh database.")
    
    # Always create new database
    logging.info("Initializing new database.")
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    try:
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.executescript(schema)
        conn.commit()
        logging.info("Database initialized successfully.")
        
    except sqlite3.Error as e:
        logging.error(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

# def main():
#     # Initialisation de la base de données
#     initialize_database()

#     # Chargement des variables d'environnement
#     env = Env()
#     Env.read_env()
#     OPEN_AI_KEY = env('OPEN_AI_KEY')

#     # Initialisation du système avec une clé API externe (placeholder)
#     system = System(external_api_key=OPEN_AI_KEY)

#     # Création des utilisateurs
#     admin_username = "super_admin_15"
#     admin_password = "AdminPass12354"
#     admin_fullname = "Super Admin 12"

#     admin_id = system.createUser(
#         username=admin_username,
#         password=admin_password,
#         fullname=admin_fullname,
#         role_names=["ADMIN"]
#     )

#     if admin_id:
#         logging.info(f"Created admin user with ID: {admin_id}")
#     else:
#         logging.error("Failed to create admin user.")
#         return

#     employee_username = "john_doe_15"
#     employee_password = "EmployeePass45627"
#     employee_fullname = "John Doe 15"

#     employee_id = system.createUser(
#         username=employee_username,
#         password=employee_password,
#         fullname=employee_fullname,
#         role_names=["EMPLOYEE"]
#     )

#     if employee_id:
#         logging.info(f"Created employee user with ID: {employee_id}")
#     else:
#         logging.error("Failed to create employee user.")
#         return

#     auditor_username = "audit_bob_11"
#     auditor_password = "AuditorPass78915"
#     auditor_fullname = "Audit Bob 11"

#     auditor_id = system.createUser(
#         username=auditor_username,
#         password=auditor_password,
#         fullname=auditor_fullname,
#         role_names=["AUDITOR"]
#     )

#     if auditor_id:
#         logging.info(f"Created auditor user with ID: {auditor_id}")
#     else:
#         logging.error("Failed to create auditor user.")
#         return
    
#     if admin_id:
#         user = get_user_by_id(admin_id)
#         system.setUserConsent(user,admin_id,True)
#         logging.info(f"Admin consent set for ID: {admin_id}")

#     if employee_id:
#         user = get_user_by_id(employee_id)
#         system.setUserConsent(user,employee_id, True)
#         logging.info(f"Employee consent set for ID: {employee_id}")

#     if auditor_id:
#         user = get_user_by_id(auditor_id)
#         system.setUserConsent(user,auditor_id, True)
#         logging.info(f"Auditor consent set for ID: {auditor_id}")


#     # 4) Authentifier chaque utilisateur
#     admin_user = system.authenticateUser(admin_username, admin_password)
#     employee_user = system.authenticateUser(employee_username, employee_password)
#     auditor_user = system.authenticateUser(auditor_username, auditor_password)

#     if admin_user and admin_user.isauthenticate():
#         logging.info("Admin authenticated successfully.")
#     else:
#         logging.error("Admin authentication failed.")
#         return

#     if employee_user and employee_user.isauthenticate():
#         logging.info("Employee authenticated successfully.")
#     else:
#         logging.error("Employee authentication failed.")
#         # Selon la logique métier, continuer ou arrêter
#         # Pour cet exemple, continuer

#     if auditor_user and auditor_user.isauthenticate():
#         logging.info("Auditor authenticated successfully.")
#     else:
#         logging.error("Auditor authentication failed.")
#         # Selon la logique métier, continuer ou arrêter

#     # 5) Créer la permission 'CONFIGURE_SYSTEM'
#     # if admin_user and admin_user.isauthenticate():
#     #     result_create_configure_system_perm = system.createPermission(admin_user, "CONFIGURE_SYSTEM", "Permission to configure the system.")
#     #     if "created with ID" in result_create_configure_system_perm:
#     #         logging.info(result_create_configure_system_perm)
#     #     else:
#     #         logging.error(result_create_configure_system_perm)
#     # else:
#     #     logging.error("Admin user is not authenticated. Cannot create 'CONFIGURE_SYSTEM' permission.")

#     # 6) Assigner la permission 'CONFIGURE_SYSTEM' au rôle 'ADMIN'
#     # configure_system_perm = get_permission_by_name("CONFIGURE_SYSTEM")
#     # admin_role = get_role_by_name("ADMIN")
#     # if configure_system_perm and admin_role:
#     #     assign_result = system.attachPermissionToRole(admin_user, admin_role["id"], configure_system_perm["id"])
#     #     if "attached to role" in assign_result:
#     #         logging.info(assign_result)
#     #     else:
#     #         logging.error(assign_result)
#     # else:
#     #     if not configure_system_perm:
#     #         logging.error("Permission 'CONFIGURE_SYSTEM' does not exist. Cannot assign to 'ADMIN' role.")
#     #     if not admin_role:
#     #         logging.error("Role 'ADMIN' does not exist. Cannot assign 'CONFIGURE_SYSTEM' permission.")

#     # 7) Admin crée un nouveau rôle : "COMPLIANCE_OFFICER"
#     if admin_user and admin_user.isauthenticate():
#         result_create_role = system.createRole(admin_user, "COMPLIANCE_OFFICER", "Handles compliance tasks")
#         if "created with ID" in result_create_role:
#             logging.info(result_create_role)
#         else:
#             logging.error(result_create_role)
#     else:
#         logging.error("Admin user is not authenticated. Cannot create role.")

#     # 8) Mise à jour de la description du rôle "COMPLIANCE_OFFICER"
#     role_data = get_role_by_name("COMPLIANCE_OFFICER")
#     if role_data:
#         role_id = role_data.get("id")
#         if role_id:
#             update_role_result = system.updateRoleDescription(admin_user, role_id, "Updated description for compliance tasks")
#             if "updated with new description" in update_role_result:
#                 logging.info(update_role_result)
#             else:
#                 logging.error(update_role_result)
#         else:
#             logging.error("Role ID not found for 'COMPLIANCE_OFFICER'.")
#     else:
#         logging.error("Could not retrieve role data for 'COMPLIANCE_OFFICER'.")

#     # 9) Créer une nouvelle permission : "MANAGE_COMPLIANCE"
#     if admin_user and admin_user.isauthenticate():
#         result_create_perm = system.createPermission(admin_user, "MANAGE_COMPLIANCE", "Able to manage GDPR or compliance operations")
#         if "created with ID" in result_create_perm:
#             logging.info(result_create_perm)
#         else:
#             logging.error(result_create_perm)
#     else:
#         logging.error("Admin user is not authenticated. Cannot create permission.")

#     # 10) Attacher la permission "MANAGE_COMPLIANCE" au rôle "COMPLIANCE_OFFICER"
#     permission_data = get_permission_by_name("MANAGE_COMPLIANCE")
#     if role_data and permission_data:
#         attach_result = system.attachPermissionToRole(admin_user, role_data["id"], permission_data["id"])
#         if "attached to role" in attach_result:
#             logging.info(attach_result)
#         else:
#             logging.error(attach_result)
#     else:
#         if not role_data:
#             logging.error("Role data for 'COMPLIANCE_OFFICER' is missing. Cannot attach permission.")
#         if not permission_data:
#             logging.error("Permission data for 'MANAGE_COMPLIANCE' is missing. Cannot attach permission.")

#     # 11) Détacher la permission "MANAGE_COMPLIANCE" du rôle "COMPLIANCE_OFFICER" (test de suppression)
#     if role_data and permission_data:
#         detach_result = system.detachPermissionFromRole(admin_user, role_data["id"], permission_data["id"])
#         if "removed from role" in detach_result:
#             logging.info(detach_result)
#         else:
#             logging.error(detach_result)
#     else:
#         logging.error("Cannot detach permission due to missing role or permission data.")

#     # 12) Supprimer la permission "MANAGE_COMPLIANCE" (pour démonstration)
#     if permission_data:
#         delete_perm_result = system.deletePermission(admin_user, permission_data["id"])
#         if "deleted" in delete_perm_result:
#             logging.info(delete_perm_result)
#         else:
#             logging.error(delete_perm_result)
#     else:
#         logging.error("Permission data for 'MANAGE_COMPLIANCE' is missing. Cannot delete permission.")

#     # 13) Supprimer le rôle "COMPLIANCE_OFFICER" (pour démonstration)
#     if role_data:
#         delete_role_result = system.deleteRole(admin_user, role_data["id"])
#         if "deleted" in delete_role_result:
#             logging.info(delete_role_result)
#         else:
#             logging.error(delete_role_result)
#     else:
#         logging.error("Role data for 'COMPLIANCE_OFFICER' is missing. Cannot delete role.")

#     # 14) Admin charge un modèle local
#     if admin_user and admin_user.isauthenticate():
#         load_model_result = system.adminLoadLocalModel(admin_user, "mistral")
#         if "successfully" in load_model_result:
#             logging.info(load_model_result)
#         else:
#             logging.error(load_model_result)
#     else:
#         logging.error("Admin user is not authenticated. Cannot load local model.")

#     # 15) Admin définit la clé API externe
#     if admin_user and admin_user.isauthenticate():
#         external_key_result = system.adminSetExternalAPIKey(admin_user, OPEN_AI_KEY)
#         if "successfully" in external_key_result:
#             logging.info(external_key_result)
#         else:
#             logging.error(external_key_result)
#     else:
#         logging.error("Admin user is not authenticated. Cannot set external API key.")

#       # 16) Employé fait une requête AI locale
#     if employee_user and employee_user.isauthenticate():
#         local_ai_response = system.makeRequest(employee_user, "Hello local AI, do you have info about user secrets?", use_external_ai=False)
#         if local_ai_response and hasattr(local_ai_response, 'content'):
#             logging.info(f"[Local AI] Response content: {local_ai_response.content}")
#         else:
#             logging.error("Failed to get response from local AI.")
#     else:
#         logging.error("Employee user is not authenticated. Cannot make local AI request.")

#     # 17) Attribution de la permission "AI_USE_EXTERNAL" à l'employé
#     if admin_user and admin_user.isauthenticate():
#         external_perm = get_permission_by_name("AI_USE_EXTERNAL")
#         if not external_perm:
#             # Création de la permission si elle n'existe pas
#             create_perm_result = system.createPermission(admin_user, "AI_USE_EXTERNAL", "Permission to use external AI")
#             if "created with ID" in create_perm_result:
#                 logging.info(create_perm_result)
#                 external_perm = get_permission_by_name("AI_USE_EXTERNAL")
#             else:
#                 logging.error("Failed to create permission 'AI_USE_EXTERNAL'.")
        
#         if external_perm:
#             employee_role_data = get_role_by_name("EMPLOYEE")
#             if employee_role_data:
#                 attach_external_perm = system.attachPermissionToRole(admin_user, employee_role_data["id"], external_perm["id"])
#                 if "attached to role" in attach_external_perm:
#                     logging.info(attach_external_perm)
#                 else:
#                     logging.error(attach_external_perm)
#             else:
#                 logging.error("Role data for 'EMPLOYEE' is missing. Cannot attach permission.")
#         else:
#             logging.error("Permission 'AI_USE_EXTERNAL' does not exist and could not be created.")
#     else:
#         logging.error("Admin user is not authenticated. Cannot grant 'AI_USE_EXTERNAL' permission.")

#     # 18) Employé fait une requête AI externe
#     if employee_user and employee_user.isauthenticate():
#         external_ai_response = system.makeRequest(employee_user, "Now I'd like help from external AI about top-secret info: 1234", use_external_ai=True)
#         if external_ai_response and hasattr(external_ai_response, 'content'):
#             logging.info(f"[External AI] Response content: {external_ai_response.content}")
#         else:
#             logging.error("Failed to get response from external AI.")
#     else:
#         logging.error("Employee user is not authenticated. Cannot make external AI request.")


#       # 9) Créer une nouvelle permission : "MANAGE_COMPLIANCE"
#     if admin_user and admin_user.isauthenticate():
#         result_create_perm = system.createPermission(admin_user, "VIEW_LOGS", "Able to view logs")
#         if "created with ID" in result_create_perm:
#             logging.info(result_create_perm)
#         else:
#             logging.error(result_create_perm)
#     else:
#         logging.error("Admin user is not authenticated. Cannot create permission.")

#     # 10) Attacher la permission "MANAGE_COMPLIANCE" au rôle "COMPLIANCE_OFFICER"
#     permission_data = get_permission_by_name("VIEW_LOGS")
#     role_data = get_role_by_name("AUDITOR")
#     if role_data and permission_data:
#         attach_result = system.attachPermissionToRole(admin_user, role_data["id"], permission_data["id"])
#         if "attached to role" in attach_result:
#             logging.info(attach_result)
#         else:
#             logging.error(attach_result)
#     else:
#         if not role_data:
#             logging.error("Role data for 'AUDITOR' is missing. Cannot attach permission.")
#         if not permission_data:
#             logging.error("Permission data for 'VIEW_LOGS' is missing. Cannot attach permission.") 

#     # 19) Auditeur récupère les logs de la base de données
#     if auditor_user and auditor_user.isauthenticate():
#         logs = system.getAllAuditLogs(auditor_user)
#         if logs is not None:
#             logging.info("\n--- AUDIT LOGS FROM DB ---")
#             for entry in logs:
#                 logging.info(entry)
#         else:
#             logging.error("Failed to retrieve audit logs.")
#     else:
#         logging.error("Auditor user is not authenticated. Cannot retrieve audit logs.")


# main.py

import os
from databaseHandler import (
    get_connection,
    execute_query,
    create_user,
    get_user_by_username,
    assign_role_to_user,
    get_roles_for_user,
    insert_audit_log,
    get_all_audit_logs,
    initialize_database
)

def test_database_connection():
    try:
        # Initialize the database (if not already initialized)
        print("Initializing the database with default permissions and roles...")
        # initialize_database()

        # Create a new test user
        print("Creating a new test user...")
        test_username = "testuser"
        test_password = "hashed_test_password"  # In practice, use a proper hashed password
        test_fullname = "Test User"
        test_department = "Testing"

        user_id = create_user(test_username, test_password, test_fullname, test_department)
        if user_id:
            print(f"Test user created with ID: {user_id}")
        else:
            print("Failed to create test user.")

        # Retrieve the test user by username
        print(f"Retrieving user '{test_username}' from the database...")
        user = get_user_by_username(test_username)
        if user:
            print("User retrieved successfully:")
            print(user)
        else:
            print("User not found.")

        # Assign ADMIN role to the test user
        print("Assigning ADMIN role to the test user...")
        admin_role = execute_query("SELECT id FROM roles WHERE name = %s", ("ADMIN",), fetchone=True)
        if admin_role:
            assign_role_to_user(user_id, admin_role['id'])
            print("ADMIN role assigned successfully.")
        else:
            print("ADMIN role not found.")

        # Retrieve roles for the test user
        print("Retrieving roles assigned to the test user...")
        roles = get_roles_for_user(user_id)
        print(f"Roles for user ID {user_id}:")
        for role in roles:
            print(role)

        # Insert an audit log entry
        print("Inserting an audit log entry...")
        action = "TEST_CONNECTION"
        details = "Successfully tested the database connection."
        insert_audit_log(user_id, action, details)
        print("Audit log entry inserted.")

        # Retrieve and display all audit logs
        print("Retrieving all audit logs...")
        audit_logs = get_all_audit_logs()
        print("Audit Logs:")
        for log in audit_logs:
            print(log)

    except Exception as e:
        print(f"An error occurred during the database connection test: {e}")

if __name__ == "__main__":
    test_database_connection()
