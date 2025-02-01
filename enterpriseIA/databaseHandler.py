# import mysql.connector
# from mysql.connector import errorcode
from datetime import datetime
import os


# ----------------------------
# Configuration
# ----------------------------

# It's recommended to use environment variables for sensitive information
DB_CONFIG = {
    'user':  'root',
    'password':  'Marcarold01*',
    'host':  'localhost',
    'database':  'enterpriseia',
    'raise_on_warnings': True
}

# ----------------------------
# Connection Handling
# ----------------------------

# def get_connection():
#     """
#     Establishes and returns a new MySQL database connection.
#     """
#     try:
#         print("here before connection")
#         conn = mysql.connector.connect(**DB_CONFIG)
#         print("here after connection")
#         return conn
#     except mysql.connector.Error as err:
#         if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#             print("Error: Invalid database credentials")
#         elif err.errno == errorcode.ER_BAD_DB_ERROR:
#             print("Error: Database does not exist")
#         else:
#             print(f"Error: {err}")
#         raise

import pymysql

def get_connection():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='Marcarold01*',
            database='enterpriseia',
            port=3306
        )
        return conn
    except Exception as err:
        print(f"Error: {err}")
        raise
# ----------------------------
# Helper Functions
# ----------------------------

def execute_query(query, params=None, fetchone=False, fetchall=False):
    """
    Executes a given SQL query with optional parameters.
    
    Args:
        query (str): The SQL query to execute.
        params (tuple): The parameters to substitute into the query.
        fetchone (bool): Whether to fetch one result.
        fetchall (bool): Whether to fetch all results.
    
    Returns:
        The fetched result(s) if fetchone or fetchall is True, else None.
    """
    conn = get_connection()
    # cursor = conn.cursor(dictionary=True)
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if fetchone:
            result = cursor.fetchone()
            return result
        if fetchall:
            results = cursor.fetchall()
            return results
        conn.commit()
    except pymysql.connect.Error as err:
        print(f"Error: {err}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

# ----------------------------
# USERS
# ----------------------------


def create_user(username: str, hashed_password: str, fullname: str = "", department: str = "") -> int:
    """
    Creates a new user in the users table.
    
    Args:
        username (str): The unique username.
        hashed_password (str): The hashed password.
        fullname (str): Full name of the user.
        department (str): Department of the user.
    
    Returns:
        int: The ID of the newly created user, or None if there's an error.
    """
    # 1) Insert user
    insert_query = """
        INSERT INTO users (username, hashed_password, fullname, department)
        VALUES (%s, %s, %s, %s)
    """
    insert_params = (username, hashed_password, fullname, department)

    print("here - about to insert user")  # Debug

    # Use your execute_query helper to insert
    execute_query(insert_query, insert_params)

    print("here - user inserted successfully")  # Debug

    # 2) Fetch the newly created user record
    #    Notice we provide the 'params' as a tuple containing (username,)
    select_query = """
        SELECT * 
        FROM users 
        WHERE username = %s
        LIMIT 1
    """
    select_params = (username,)
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(select_query, select_params)  # Now we actually pass the params
        row = cursor.fetchone()
        print(row[0])
        new_id = row[0] if row else None
        print("here - user found in DB" if row else "here - user not found in DB")
    except pymysql.connect.Error as err:
        print(f"Error retrieving last insert ID: {err}")
        new_id = None
        #conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return new_id




def get_user_by_id(user_id: int):
    """
    Retrieves a user by their ID.
    
    Args:
        user_id (int): The user's ID.
    
    Returns:
        dict or None: User details or None if not found.
    """
    query = """
        SELECT id, username, hashed_password, fullname, department, created_at
        FROM users
        WHERE id = %s
    """
    params = (user_id,)
    result = execute_query(query, params, fetchone=True)
    return result

def get_user_by_username(username: str):
    """
    Retrieves a user by their username.
    
    Args:
        username (str): The user's username.
    
    Returns:
        dict or None: User details or None if not found.
    """
    query = """
        SELECT id, username, hashed_password, fullname, department, created_at
        FROM users
        WHERE username = %s
    """
    params = (username,)
    result = execute_query(query, params, fetchone=True)
    return result

# ----------------------------
# ROLES
# ----------------------------

def create_role(name: str, description: str = "") -> int:
    """
    Creates a new role or retrieves the existing role's ID if it already exists.
    
    Args:
        name (str): The unique name of the role.
        description (str): Description of the role.
    
    Returns:
        int: The ID of the role.
    """
    query = """
        INSERT INTO roles (name, description)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
    """
    params = (name, description)
    execute_query(query, params)
    
    # Retrieve the role ID
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT LAST_INSERT_ID() AS id")
        row = cursor.fetchone()
        role_id = row[0] if row else None
    except pymysql.connect.Error as err:
        print(f"Error retrieving role ID: {err}")
        role_id = None
    finally:
        cursor.close()
        conn.close()
    return role_id

def get_role_by_id(role_id: int):
    """
    Retrieves a role by its ID.
    
    Args:
        role_id (int): The role's ID.
    
    Returns:
        dict or None: Role details or None if not found.
    """
    query = """
        SELECT id, name, description
        FROM roles
        WHERE id = %s
    """
    params = (role_id,)
    result = execute_query(query, params, fetchone=True)
    return result

def get_role_by_name(name: str):
    """
    Retrieves a role by its name.
    
    Args:
        name (str): The role's name.
    
    Returns:
        dict or None: Role details or None if not found.
    """
    query = """
        SELECT id, name, description
        FROM roles
        WHERE name = %s
    """
    params = (name,)
    result = execute_query(query, params, fetchone=True)
    return result

def update_role_description(role_id: int, new_description: str):
    """
    Updates the description of a role.
    
    Args:
        role_id (int): The role's ID.
        new_description (str): The new description.
    """
    query = """
        UPDATE roles
        SET description = %s
        WHERE id = %s
    """
    params = (new_description, role_id)
    execute_query(query, params)

def delete_role(role_id: int):
    """
    Deletes a role by its ID.
    
    Args:
        role_id (int): The role's ID.
    """
    query = "DELETE FROM roles WHERE id = %s"
    params = (role_id,)
    execute_query(query, params)

# ----------------------------
# PERMISSIONS
# ----------------------------

def create_permission(name: str, description: str = "") -> int:
    """
    Creates a new permission.
    
    Args:
        name (str): The unique name of the permission.
        description (str): Description of the permission.
    
    Returns:
        int: The ID of the newly created permission.
    """
    query = """
        INSERT INTO permissions (name, description)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)
    """
    params = (name, description)
    execute_query(query, params)
    
    # Retrieve the permission ID
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT LAST_INSERT_ID() AS id")
        row = cursor.fetchone()
        permission_id = row[0] if row else None
    except pymysql.connect.Error as err:
        print(f"Error retrieving permission ID: {err}")
        permission_id = None
    finally:
        cursor.close()
        conn.close()
    return permission_id

def get_permission_by_id(permission_id: int):
    """
    Retrieves a permission by its ID.
    
    Args:
        permission_id (int): The permission's ID.
    
    Returns:
        dict or None: Permission details or None if not found.
    """
    query = """
        SELECT id, name, description
        FROM permissions
        WHERE id = %s
    """
    params = (permission_id,)
    result = execute_query(query, params, fetchone=True)
    return result

def get_permission_by_name(name: str):
    """
    Retrieves a permission by its name.
    
    Args:
        name (str): The permission's name.
    
    Returns:
        dict or None: Permission details or None if not found.
    """
    query = """
        SELECT id, name, description
        FROM permissions
        WHERE name = %s
    """
    params = (name,)
    result = execute_query(query, params, fetchone=True)
    return result

def update_permission_description(permission_id: int, new_description: str):
    """
    Updates the description of a permission.
    
    Args:
        permission_id (int): The permission's ID.
        new_description (str): The new description.
    """
    query = """
        UPDATE permissions
        SET description = %s
        WHERE id = %s
    """
    params = (new_description, permission_id)
    execute_query(query, params)

def delete_permission(permission_id: int):
    """
    Deletes a permission by its ID.
    
    Args:
        permission_id (int): The permission's ID.
    """
    query = "DELETE FROM permissions WHERE id = %s"
    params = (permission_id,)
    execute_query(query, params)

# ----------------------------
# USER-ROLES (Many-to-Many)
# ----------------------------

def assign_role_to_user(user_id: int, role_id: int):
    """
    Assigns a role to a user.
    
    Args:
        user_id (int): The user's ID.
        role_id (int): The role's ID.
    """
    query = """
        INSERT INTO user_roles (user_id, role_id)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE id = id
    """
    params = (user_id, role_id)
    execute_query(query, params)

def get_roles_for_user(user_id: int):
    """
    Retrieves all roles assigned to a user.
    
    Args:
        user_id (int): The user's ID.
    
    Returns:
        list of dict: List of roles.
    """
    query = """
        SELECT r.id, r.name, r.description
        FROM roles r
        INNER JOIN user_roles ur ON ur.role_id = r.id
        WHERE ur.user_id = %s
    """
    params = (user_id,)
    results = execute_query(query, params, fetchall=True)
    return results if results else []

def remove_role_from_user(user_id: int, role_id: int):
    """
    Removes a role from a user.
    
    Args:
        user_id (int): The user's ID.
        role_id (int): The role's ID.
    """
    query = """
        DELETE FROM user_roles
        WHERE user_id = %s AND role_id = %s
    """
    params = (user_id, role_id)
    execute_query(query, params)

# ----------------------------
# ROLE-PERMISSIONS (Many-to-Many)
# ----------------------------

def assign_permission_to_role(role_id: int, permission_id: int):
    """
    Assigns a permission to a role.
    
    Args:
        role_id (int): The role's ID.
        permission_id (int): The permission's ID.
    """
    query = """
        INSERT INTO role_permissions (role_id, permission_id)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE id = id
    """
    params = (role_id, permission_id)
    execute_query(query, params)

def get_permissions_for_role(role_id: int):
    """
    Retrieves all permissions assigned to a role.
    
    Args:
        role_id (int): The role's ID.
    
    Returns:
        list of dict: List of permissions.
    """
    query = """
        SELECT p.id, p.name, p.description
        FROM permissions p
        INNER JOIN role_permissions rp ON rp.permission_id = p.id
        WHERE rp.role_id = %s
    """
    params = (role_id,)
    results = execute_query(query, params, fetchall=True)
    return results if results else []

def remove_permission_from_role(role_id: int, permission_id: int):
    """
    Removes a permission from a role.
    
    Args:
        role_id (int): The role's ID.
        permission_id (int): The permission's ID.
    """
    query = """
        DELETE FROM role_permissions
        WHERE role_id = %s AND permission_id = %s
    """
    params = (role_id, permission_id)
    execute_query(query, params)

# ----------------------------
# REQUESTS / RESPONSES / AUDIT
# ----------------------------

def insert_request(request_id: str, user_id: int, content: str):
    """
    Inserts a new request.
    
    Args:
        request_id (str): The unique request ID (e.g., UUID).
        user_id (int): The ID of the user making the request.
        content (str): The content of the request.
    """
    query = """
        INSERT INTO requests (id, user_id, content)
        VALUES (%s, %s, %s)
    """
    params = (request_id, user_id, content)
    execute_query(query, params)

def insert_response(request_id: str, content: str):
    """
    Inserts a new response to a request.
    
    Args:
        request_id (str): The ID of the request.
        content (str): The content of the response.
    """
    query = """
        INSERT INTO responses (request_id, content)
        VALUES (%s, %s)
    """
    params = (request_id, content)
    execute_query(query, params)

def insert_audit_log(user_id: int, action: str, details: str = ""):
    """
    Inserts a new audit log entry.
    
    Args:
        user_id (int): The ID of the user performing the action.
        action (str): The action performed.
        details (str): Additional details about the action.
    """
    query = """
        INSERT INTO audit_logs (user_id, action, details)
        VALUES (%s, %s, %s)
    """
    params = (user_id, action, details)
    execute_query(query, params)

def get_all_audit_logs():
    """
    Retrieves all audit logs ordered by creation time descending.
    
    Returns:
        list of dict: List of audit log entries.
    """
    query = """
        SELECT id, user_id, action, details, created_at
        FROM audit_logs
        ORDER BY created_at DESC
    """
    results = execute_query(query, fetchall=True)
    return results if results else []
    
def get_all_permissions():
    """
        Retrieves all permission records from the 'permissions' table.
        Returns:
            A list of dictionaries, where each dictionary represents a permission.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM permissions")
    permissions = cursor.fetchall()
    conn.close()
    return permissions

def get_all_roles():
    """
        Retrieves all roles records from the 'roles' table.
        Returns:
            A list of tuple, where each tuple represents a role.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM roles")
    permissions = cursor.fetchall()
    conn.close()
    return permissions
        
# ----------------------------
# CONSENTS
# ----------------------------

def set_user_consent(user_id: int, consent: bool):
    """
    Records or updates a user's consent status.
    
    Args:
        user_id (int): The user's ID.
        consent (bool): True if consented, False otherwise.
    """
    query = """
        INSERT INTO consents (user_id, has_consented)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE has_consented = VALUES(has_consented), updated_at = CURRENT_TIMESTAMP
    """
    params = (user_id, 1 if consent else 0)
    execute_query(query, params)

def get_user_consent(user_id: int):
    """
    Retrieves a user's consent status.
    
    Args:
        user_id (int): The user's ID.
    
    Returns:
        dict or None: Consent details or None if not found.
    """
    query = """
        SELECT user_id, has_consented, updated_at
        FROM consents
        WHERE user_id = %s
    """
    params = (user_id,)
    result = execute_query(query, params, fetchone=True)
    return result

# ----------------------------
# INITIALIZATION FUNCTIONS (Optional)
# ----------------------------

def initialize_permissions():
    """
    Inserts initial permissions into the permissions table.
    """
    permissions = [
        ('CONFIGURE_SYSTEM', 'Permission to configure the system.'),
        ('USE_IA', 'Permission to use local AI'),
        ('AI_USE_EXTERNAL', 'Permission to use external AI')
    ]
    query = """
        INSERT INTO permissions (name, description)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE id = id
    """
    cursor = None
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.executemany(query, permissions)
        conn.commit()
    except pymysql.connect.Error as err:
        print(f"Error initializing permissions: {err}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def initialize_roles_and_permissions():
    """
    Initializes roles and assigns permissions to them.
    """
    # Initialize ADMIN role
    admin_role_id = create_role('ADMIN', 'Administrator role')
    
    # Assign CONFIGURE_SYSTEM to ADMIN
    configure_system_permission = get_permission_by_name('CONFIGURE_SYSTEM')
    if configure_system_permission:
        assign_permission_to_role(admin_role_id, configure_system_permission['id'])
    
    # Initialize EMPLOYEE role
    employee_role_id = create_role('EMPLOYEE', 'Default employee role')
    
    # Assign USE_IA to EMPLOYEE
    use_ia_permission = get_permission_by_name('USE_IA')
    if use_ia_permission:
        assign_permission_to_role(employee_role_id, use_ia_permission['id'])

def initialize_database():
    """
    Initializes the database with default permissions and roles.
    """
    initialize_permissions()
    initialize_roles_and_permissions()
    print("Database initialized with default permissions and roles.")

# ----------------------------
# Example Usage (For Testing)
# ----------------------------

if __name__ == "__main__":
    # Initialize the database (run once)
    # initialize_database()
    
    # Create a new user
    user_id = create_user("johndoe", "hashed_password123", "John Doe", "Engineering")
    print(f"Created user with ID: {user_id}")
    
    # Assign ADMIN role to the new user
    admin_role = get_role_by_name("ADMIN")
    if admin_role:
        assign_role_to_user(user_id, admin_role['id'])
        print(f"Assigned ADMIN role to user ID: {user_id}")
    
    # Insert an audit log
    insert_audit_log(user_id, "CREATE_USER", "Created a new user and assigned ADMIN role.")
    
    # Retrieve and print audit logs
    audit_logs = get_all_audit_logs()
    for log in audit_logs:
        print(log)
