if __name__ != '__main__':
    from helpers.fetch import empty_or_row, empty_or_rows
    from helpers.hash import hash_md5, hash_sha256
from flask import Response, Request, json
from mysql.connector import MySQLConnection
from mysql.connector.connection import MySQLCursorDict
from random import choice


def login(db: MySQLConnection, cursor: MySQLCursorDict, request_body):
    cursor.execute(
        f"""
        SELECT id_user, name, phone, email, address, password, id_role
        FROM user WHERE email = '{request_body.get('email_or_phone')}';
        """
    )
    user_data = empty_or_row(cursor)

    if not user_data:
        cursor.execute(
            f"""
            SELECT id_user, name, phone, email, address, password, id_role
            FROM user WHERE phone = '{request_body.get('email_or_phone')}';
            """
        )
        user_data = empty_or_row(cursor)

        if not user_data:
            return Response(
                mimetype="application/json",
                status=404,
                response=json.dumps({'status': "GALAT", 'message': "User tidak terdaftar..."})
            )

    try:
        user_credentials = {
            'email_or_phone': request_body['email_or_phone'],
            'password': request_body['password']
        }
    except ValueError:
        return Response(
            mimetype="application/json",
            status=404,
            response=json.dumps({'status': "GALAT", 'message': "email atau password salah..."})
        )

    if user_data['password'] != hash_sha256(user_credentials['password']):
        return Response(
            mimetype="application/json",
            status=404,
            response=json.dumps({'status': "GALAT", 'message': "email atau password salah..."})
        )

    cursor.execute(
        f"""
        INSERT INTO token(token, expired_in, id_user)
        VALUES(
            {hash_md5("".join(choice(request_body['email_or_phone'])))},
            NOW() + INTERVAL 3 DAY,
            '{user_data['id_user']}'
        )
        """
    )

    return Response(
        mimetype="application/json",
        status=200,
        response=json.dumps({'status': "OK", 'message': "Login berhasil!"})
    )
