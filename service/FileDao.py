from datetime import datetime
from unittest import result

from utils.DatabaseUtil import get_db_connection

def insert_file(file_id, filename, size, extension, storage_url):
    conn = get_db_connection()

    sql = """
        INSERT INTO file (id, filename, size, extension, storage_url, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    parameters = (file_id, filename, size, extension, storage_url, datetime.now())

    cursor = conn.cursor()
    cursor.execute(sql, parameters)
    conn.commit()
    conn.close()


def get_blob_name(file_url):
    conn = get_db_connection()

    sql = """
        SELECT id, extension FROM file WHERE storage_url = %s
    """

    cursor = conn.cursor()
    cursor.execute(sql, (file_url,))
    file_id, extension = cursor.fetchone()
    conn.close()

    return f"{file_id}.{extension}"


def delete_file(file_url):
    conn = get_db_connection()

    sql = """
        DELETE FROM file WHERE storage_url = %s
    """

    cursor = conn.cursor()
    cursor.execute(sql, (file_url,))
    conn.commit()
    conn.close()


