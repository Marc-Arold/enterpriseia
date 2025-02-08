import datetime
from databaseHandler import (
    get_connection,
    insert_audit_log,
    get_user_consent
)

class ComplianceModule:
    def __init__(self, retention_days=90):
        """
        :param retention_days: how many days to keep data (requests, responses).
        """
        self.retention_days = retention_days

    def has_valid_consent(self, user_id: int) -> bool:
        """
        Check if the user has given consent for AI processing.
        This example expects a 'consents' table or an added column in 'users'.
        Return True if the user has not revoked consent.
        """
        # conn = get_connection()
        # cursor = conn.cursor()
      
        # cursor.execute("SELECT has_consented FROM consents WHERE user_id = %s", (user_id,))
        # row = cursor.fetchone()
        # conn.close()
        row = get_user_consent(user_id=user_id)
        print("user ID", user_id)
        print("row",row)
        if not row:
            return False
        # return bool(row[0])
        return row[1]==1

    def enforce_data_retention(self):
        """
        Delete old records from requests, responses, and/or audit_logs
        if they exceed the retention period.
        """
        conn = get_connection()
        cursor = conn.cursor()

        cutoff = datetime.datetime.now() - datetime.timedelta(days=self.retention_days)
        cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            DELETE FROM requests
            WHERE created_at < %s
        """, (cutoff_str,))

        cursor.execute("""
            DELETE FROM responses
            WHERE created_at < %s
        """, (cutoff_str,))

        conn.commit()
        conn.close()

    def erase_user_data(self, user_id: int, acting_user_id: int):
        """
        Implements 'right to be forgotten'. Removes the user's records from
        requests, responses, and consents. Logs the action.
        """
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM requests WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM consents WHERE user_id = %s", (user_id,))

        conn.commit()
        conn.close()

        insert_audit_log(
            acting_user_id,
            "ERASE_USER_DATA",
            f"Erased data for user_id={user_id}"
        )
