import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv

def get_connection(db_config):
    """
    Établit une connexion à la base de données MySQL spécifiée.

    Args:
        db_config (dict): Dictionnaire contenant les paramètres de connexion.

    Returns:
        mysql.connector.connection.MySQLConnection: Objet de connexion MySQL.
    """
    try:
        print("Établissement de la connexion à MySQL...")
        conn = mysql.connector.connect(**db_config)
        print("Connexion réussie à la base de données 'enterpriseIA'.")
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erreur : Accès refusé. Vérifiez votre nom d'utilisateur ou votre mot de passe.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Erreur : La base de données spécifiée n'existe pas.")
        else:
            print(f"Erreur MySQL : {err}")
        return None

def test_connection(conn):
    """
    Effectue une requête simple pour tester la connexion à la base de données.

    Args:
        conn (mysql.connector.connection.MySQLConnection): Objet de connexion MySQL.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        db = cursor.fetchone()
        print(f"Vous êtes connecté à la base de données : {db[0]}")
        
        # Exemple de requête: lister les tables
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("Tables présentes dans la base de données :")
        for table in tables:
            print(f"- {table[0]}")
        
    except mysql.connector.Error as err:
        print(f"Erreur lors de l'exécution de la requête : {err}")
    finally:
        cursor.close()

def main():
    """
    Fonction principale pour établir la connexion et tester l'accès à la base de données.
    """
    # ----------------------------
    # Configuration
    # ----------------------------

    # Charger les variables d'environnement depuis un fichier .env (optionnel mais recommandé)
    load_dotenv()

    # Paramètres de connexion à la base de données depuis les variables d'environnement
    db_config = {
        'user': os.getenv('DB_USER', 'root'),               
        'password': os.getenv('DB_PASSWORD', 'Marcarold01*'),
        'host': os.getenv('DB_HOST', 'localhost'),          
        'database': os.getenv('DB_NAME', 'enterpriseIA'),    
        'port': int(os.getenv('DB_PORT', 3306))              
    }

    print("Lancement du script de connexion à la base de données 'enterpriseIA'.")

    # ----------------------------
    # Établir la connexion
    # ----------------------------

    conn = get_connection(db_config)

    if conn:
        # ----------------------------
        # Tester la connexion
        # ----------------------------
        test_connection(conn)
        
        # ----------------------------
        # Fermer la connexion
        # ----------------------------
        conn.close()
        print("Connexion MySQL fermée.")
    else:
        print("Échec de la connexion à la base de données.")

if __name__ == "__main__":
    main()
