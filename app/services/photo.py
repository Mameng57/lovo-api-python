if __name__ != '__main__':
    from helpers.fetch import empty_or_row, empty_or_rows
from os import path
from flask import Flask, Response, Request, json, send_file
from mysql.connector import MySQLConnection
from mysql.connector.connection import MySQLCursorDict
from werkzeug.utils import secure_filename


ALLOWED_EXTENSION = ["jpg", "jpeg", "png", "webp", "bmp"]


def allowed_file(filename: str):
    if filename.split('.')[1].lower() in ALLOWED_EXTENSION:
        return True

    return False


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


def get_all_photo(cursor: MySQLCursorDict, id: int):
    cursor.execute(
        f"""
        SELECT id_photo, url, id_session FROM photo WHERE id_session = {id}
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


def upload_photo(app: Flask, db: MySQLConnection, cursor: MySQLCursorDict, request: Request, id: int):
    if 'file' not in request.files:
        return Response(
            mimetype="application/json",
            status=400,
            response=json.dumps({'status': "GALAT", 'message': "Argument file kosong..."})
        )

    file = request.files['file']

    if not file.filename:
        return Response(
            mimetype="application/json",
            status=400,
            response=json.dumps({'status': "GALAT", 'message': "Nama File kosong..."})
        )

    if file and allowed_file(file.filename):
        filename = path.join(app.config['UPLOAD_FOLDER'], secure_filename(f"{id}_{file.filename}"))
        db_file_path = f"static/uploads/{id}_{file.filename}"
        file.save(filename)
        cursor.execute(
            f"""
            INSERT INTO photo(url, id_session)
            VALUES('{db_file_path}', {id})
            """
        )
        db.commit()

        return Response(
            mimetype="application/json",
            status=200,
            response=json.dumps({'status': "OK", 'message': "Upload foto berhasil!"})
        )

    return Response(
        mimetype="application/json",
        status=500,
        response=json.dumps({'status': "GALAT", 'message': "Server tidak dapat menerima file itu..."})
    )


def view_photo(file_path: str):
    match file_path.split('.')[1].lower():
        case "png":
            return send_file(file_path, mimetype="image/png")
        case "bmp":
            return send_file(file_path, mimetype="image/bmp")
        case "webp":
            return send_file(file_path, mimetype="image/webp")

    return send_file(file_path, mimetype="image/jpeg")
