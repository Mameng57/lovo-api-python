from flask import Flask, Response, request, jsonify
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from services.user import get_all_user, get_user, create_user, update_user, delete_user


if __name__ == '__main__':
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False

    mysql = MySQLConnection()
    mysql.connect(
        host="localhost", user="root", password="", database="lovo-db"
    )

    if mysql.is_connected():
        print(" * Database connected!")

    cursor = MySQLCursor(mysql)


    @app.route("/", methods=["GET"])
    def test() -> Response:
        return jsonify({'status': "OK", 'message': "Terhubung dengan database!"})

    @app.route("/user", methods=["GET", "POST"])
    def user_get_create_handler() -> Response:
        if request.method == "POST":
            result = create_user(mysql, cursor, request.form)
            return result

        return get_all_user(cursor)

    @app.route("/user/<int:id>", methods=["GET", "PUT", "DELETE"])
    def user_update_delete_handler(id: int):
        if request.method == "PUT":
            result = update_user(mysql, cursor, id, request)
            return result
        if request.method == "DELETE":
            result = delete_user(mysql, cursor, id)
            return result

        return get_user(cursor, id)

    app.run(debug=True)
