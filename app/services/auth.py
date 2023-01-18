if __name__ != '__main__':
    from helpers.fetch import empty_or_row
    from helpers.hash import hash_sha256
    from helpers.tokenization import generate_token
from flask import Response, json, session
from mysql.connector import MySQLConnection
from mysql.connector.connection import MySQLCursorDict
from datetime import date


def authenticate(db: MySQLConnection, cursor: MySQLCursorDict):
    if not session.get('token'):
        return {}

    cursor.execute(
        f"""
        SELECT id_token, token, expired_in, id_user FROM token
        WHERE token = '{session.get('token')}';
        """
    )
    session_data = empty_or_row(cursor)

    if not session_data:
        return {}

    if date.today() >= session_data['expired_in']:
        log_out(db, cursor)
        return {}

    cursor.execute(
        f"""
        SELECT id_user, name, phone, email, address, password, id_role FROM user
        WHERE id_user = {session_data.get('id_user')};
        """
    )
    session_user = empty_or_row(cursor)

    return session_user


def login(db: MySQLConnection, cursor: MySQLCursorDict, request_body):
    logged_in_user = authenticate(db, cursor)

    if logged_in_user:
         return Response(
            mimetype="application/json",
            status=200,
            response=json.dumps(
                {
                    'status': "OK",
                    'message': "Login dari session!",
                    'user': {
                        'id_user': logged_in_user['id_user'],
                        'name': logged_in_user['name'],
                        'phone': logged_in_user['phone'],
                        'email': logged_in_user['email'],
                        'address': logged_in_user['address']
                    }
                }
            )
        )

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
    except KeyError:
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

    session_token = generate_token(request_body['email_or_phone'])
    session['token'] = session_token

    cursor.execute(
        f"""
        INSERT INTO token(token, expired_in, id_user)
        VALUES(
            '{session_token}',
            NOW() + INTERVAL 3 DAY,
            '{user_data['id_user']}'
        )
        """
    )
    db.commit()

    return Response(
        mimetype="application/json",
        status=200,
        response=json.dumps(
            {
                'status': "OK",
                'message': "Login berhasil!",
                'user': {
                    'id_user': user_data['id_user'],
                    'name': user_data['name'],
                    'phone': user_data['phone'],
                    'email': user_data['email'],
                    'address': user_data['address'],
                    'id_role': user_data['id_role']
                }
            }
        )
    )


def log_out(db: MySQLConnection, cursor: MySQLCursorDict):
    cursor.execute(
        f"""
        DELETE FROM token WHERE token = '{session.get('token')}';
        """
    )
    db.commit()

    session['token'] = None
    session.pop('token')

    return Response(
        mimetype="application/json",
        status=200,
        response=json.dumps({'status': "OK", 'message': "Logout berhasil!"})
    )
