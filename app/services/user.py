if __name__ != '__main__':
    from helpers.fetch import empty_or_row, empty_or_rows
    from helpers.hash import hash_sha256
from flask import Response, Request, json, jsonify
from mysql.connector import MySQLConnection, IntegrityError
from mysql.connector.cursor import MySQLCursorDict


def get_all_user(cursor: MySQLCursorDict):
    cursor.execute(
        """
        SELECT id_user, name, phone, email, address, name_role FROM user
        JOIN role ON role.id_role = user.id_role;
        """
    )
    rows = empty_or_rows(cursor)
    data = "Data kosong..."

    if rows:
        data = rows

    return jsonify({'status': "OK", 'data': data})


def get_user(cursor: MySQLCursorDict, id: int):
    status_code = 404
    response = {}
    response['status'] = "GALAT"
    response['message'] = "Data tidak ditemukan..."

    cursor.execute(
        f"""
        SELECT id_user, name, phone, email, address, name_role FROM user
        JOIN role ON role.id_role = user.id_role
        WHERE id_user = '{id}';
        """
    )
    row = empty_or_row(cursor)

    if row:
        status_code = 200
        response['status'] = "OK"
        response['message'] = "Data ditemukan!"
        response['data'] = {
            'id': row['id_user'], 'name': row['name'], 'phone': row['phone'],
            'email': row['email'], 'address': row['address'], 'role': row['name_role']
        }

    return Response(
        mimetype='application/json',
        status=status_code,
        response=json.dumps(response)
    )


def create_user(db: MySQLConnection, cursor: MySQLCursorDict, request_body):
    status_code = 400
    response = {'status': "GALAT", 'message': "Gagal menambahkan data..."}

    try:
        cursor.execute(
            f"""
            INSERT INTO user(name, phone, email, password, address, id_role)
            VALUES(
                "{request_body.get('name')}", "{request_body.get('phone')}",
                "{request_body.get('email')}",
                "{hash_sha256(request_body.get('password'))}",
                "{request_body.get('address')}", {request_body.get('id_role')}
            );
            """
        )
        db.commit()

        status_code = 200
        response['status'] = "OK"
        response['message'] = "Berhasil menambahkan data!"
    except IntegrityError:
        response['message'] = "Email sudah terdaftar atau value salah..."
    except AttributeError:
        response['message'] = "Value kurang, coba periksa parameter yang diperlukan..."

    return Response(
        mimetype='application/json',
        status=status_code,
        response=json.dumps(response)
    )


def update_user(db: MySQLConnection, cursor: MySQLCursorDict, id: int, request: Request):
    status_code = 400
    response = {'status': "GALAT", 'message': "Gagal mengubah data..."}

    cursor.execute(
        f"""
        SELECT id_user, name, phone, email, address, password, id_role
        FROM user WHERE id_user = {id};
        """
    )
    current_user_data = empty_or_row(cursor)

    if not current_user_data:
        return Response(
            mimetype='application/json',
            status=404,
            response=json.dumps({'status': "GALAT", 'message': "Data tidak ada..."})
        )

    new_user_data = {
        'id_user': current_user_data['id_user'],
        'name': current_user_data['name'],
        'phone': current_user_data['phone'],
        'email': current_user_data['email'],
        'address': current_user_data['address'],
        'password': current_user_data['password'],
        'id_role': current_user_data['id_role']
    }

    if request.form.get('id'):
        new_user_data['id_user'] = request.form['id']
    
    if request.form.get('name'):
        new_user_data['name'] = request.form['name']

    if request.form.get('phone'):
        new_user_data['phone'] = request.form['phone']

    if request.form.get('email'):
        new_user_data['email'] = request.form['email']

    if request.form.get('address'):
        new_user_data['address'] = request.form['address']

    if request.form.get('password'):
        new_user_data['password'] = request.form['password']

    if request.form.get('id_role'):
        new_user_data['id_role'] = request.form['id_role']

    cursor.execute(
        f"""
        UPDATE user SET id_user = {new_user_data['id_user']},
                        name = "{new_user_data['name']}",
                        phone = "{new_user_data['phone']}",
                        email = "{new_user_data['email']}",
                        address = "{new_user_data['address']}",
                        password = "{hash_sha256(new_user_data['password'])}",
                        id_role = {new_user_data['id_role']}
        WHERE id_user = {id};
        """
    )
    db.commit()

    if cursor.rowcount > 0:
        status_code = 200
        response['status'] = "OK"
        response['message'] = "Berhasil mengubah data!"

    return Response(
        mimetype='application/json',
        status=status_code,
        response=json.dumps(response)
    )


def delete_user(db: MySQLConnection, cursor: MySQLCursorDict, id: int):
    status_code = 200

    cursor.execute(f"SELECT id_user FROM user WHERE id_user = {id};")

    if not empty_or_row(cursor):
        return Response(
            mimetype='application/json',
            status=404,
            response=json.dumps({'status': "GALAT", 'message': "Data tidak ada..."})
        )

    cursor.execute(f"DELETE FROM user WHERE id_user = {id}")
    db.commit()

    return Response(
        mimetype='application/json',
        status=status_code,
        response=json.dumps({'status': "OK", 'message': "Data berhasil dihapus..."})
    )
