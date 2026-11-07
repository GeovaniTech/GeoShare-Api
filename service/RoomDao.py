import uuid
from datetime import datetime
from random import randint

from psycopg2.extras import RealDictCursor

from utils.DatabaseUtil import get_db_connection


def create_room(client_id):
    while True:
        room_id = str(randint(100000, 999999))

        if exists_room(room_id):
            continue
        else:
            break

    conn = get_db_connection()

    sql = """
        INSERT INTO room (id, created_at, client_id)
        VALUES (%s, %s, %s)
    """

    parameters = (room_id, datetime.now(), client_id)

    cursor = conn.cursor()
    cursor.execute(sql, parameters)
    conn.commit()
    conn.close()

    return room_id


def exists_room(room_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
        SELECT * FROM room WHERE id = %s
    """

    parameters = (room_id,)
    cursor.execute(sql, parameters)

    room = cursor.fetchone()

    conn.close()

    return room is not None


def add_files_to_room(room_id, files):
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
        INSERT INTO room_files (id, room_id, file_id)
        VALUES (%s, %s, %s)
    """


    for file_id in files:
         parameters = (str(uuid.uuid4()), room_id, file_id)
         cursor.execute(sql, parameters)

    conn.commit()
    conn.close()


def find_room(room_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    sql = """
        SELECT id, created_at FROM room WHERE id = %s
    """

    cursor.execute(sql, (room_id,))
    room = cursor.fetchone()

    conn.close()

    return room


def find_room_files(room_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    sql = """
        SELECT f.id, f.filename, f.extension, f.size, f.storage_url, f.created_at
        FROM room_files rf
        INNER JOIN file f ON f.id = rf.file_id
        WHERE rf.room_id = %s
        ORDER BY f.created_at
    """

    cursor.execute(sql, (room_id,))
    files = cursor.fetchall()

    conn.close()

    return files


def delete_file_from_rooms(file_url):
    conn = get_db_connection()

    sql = """
        DELETE FROM room_files WHERE file_id = (
            SELECT id FROM file WHERE storage_url = %s
        )
    """

    cursor = conn.cursor()
    cursor.execute(sql, (file_url,))
    conn.commit()
    conn.close()
