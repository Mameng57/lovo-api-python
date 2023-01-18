if __name__ != '__main__':
    from helpers.fetch import empty_or_row, empty_or_rows
from flask import Response, json
from mysql.connector.connection import MySQLCursorDict
from datetime import datetime


def get_all_session(cursor: MySQLCursorDict, id: int):
    cursor.execute(
        f"""
        SELECT id_session, date, package_info, photos_count, id_user
        FROM session WHERE id_user = {id};
        """
    )
    sessions = empty_or_rows(cursor)

    data = "Data Kosong..."

    if sessions:
        data = sessions
        for value in data:
            value['date'] = str(value['date'])

    return Response(
        mimetype="application/json",
        status=200,
        response=json.dumps({'status': "OK", 'session': data})
    )


def get_photo(cursor: MySQLCursorDict, id: int):
    cursor.execute(
        f"""
        SELECT id_photo, url FROM photo WHERE id_session = {id}
        """
    )
    photos = empty_or_rows(cursor)

    data = "Tidak ada foto..."

    if photos:
        data = photos
    
    return Response(
        mimetype="application/json",
        status=200,
        response=json.dumps({'status': "OK", 'photo': data})
    )
