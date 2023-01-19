from flask import Flask, Response, json, request, jsonify
from flask_session import Session
from mysql.connector import MySQLConnection, DatabaseError, ProgrammingError
from mysql.connector.cursor import MySQLCursorDict
from services.auth import login, log_out
from services.user import get_all_user, get_user, create_user, update_user, delete_user
from services.photo import get_all_session, get_all_photo, upload_photo, view_photo


if __name__ == '__main__':
    app = Flask(__name__)
    app.secret_key = "secret-key"
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_TYPE'] = "filesystem"
    app.config['JSON_SORT_KEYS'] = False
    app.config['UPLOAD_FOLDER'] = "app/static/uploads"

    mysql = MySQLConnection(host="localhost", user="root", password="", database="lovo-db")

    if mysql.is_connected():
        print(" * Database connected!")

    cursor = MySQLCursorDict(connection=mysql)
    Session(app=app)


    @app.route("/", methods=["GET"])
    def test() -> Response:
        return jsonify({'status': "OK", 'message': "Terhubung dengan database!"})

    @app.route("/login", methods=["POST"])
    def login_handler() -> Response:
        return login(mysql, cursor, request.form)

    @app.route("/logout", methods=["POST"])
    def logout_handler() -> Response:
        return log_out(mysql, cursor)

    @app.route("/user", methods=["GET", "POST"])
    def user_get_create_handler() -> Response:
        if request.method == "POST":
            return create_user(mysql, cursor, request.form)

        return get_all_user(cursor)

    @app.route("/user/<int:id>", methods=["GET", "PUT", "DELETE"])
    def user_update_delete_handler(id: int) -> Response:
        if request.method == "PUT":
            return update_user(mysql, cursor, id, request)
        if request.method == "DELETE":
            return delete_user(mysql, cursor, id)

        return get_user(cursor, id)

    @app.route("/session/<int:id>", methods=["POST"])
    def get_session_handler(id: int) -> Response:
        return get_all_session(cursor, id)

    @app.route("/photo/<int:id>", methods=["GET", "POST"])
    def get_photo_handler(id: int) -> Response:
        if request.method == "POST":
            return upload_photo(app, mysql, cursor, request, id)
        return get_all_photo(cursor, id)

    @app.route("/photo/<path:path>", methods=["POST"])
    def view_photo_handler(path: str) -> Response:
        return view_photo(path)

    @app.errorhandler(DatabaseError)
    def db_error_handler(error) -> Response:
        return Response(
            mimetype="application/json",
            status=500,
            response=json.dumps(
                {'status': "GALAT", 'message': "Terjadi kesalahan pada server..."}
            )
        )

    @app.errorhandler(ProgrammingError)
    def programming_error_handler(error) -> Response:
        return Response(
            mimetype="application/json",
            status=400,
            response=json.dumps(
                {
                    'status': "GALAT",
                    'message': "Value atau argument salah, harap periksa kembali..."
                }
            )
        )

    @app.errorhandler(404)
    def not_found_error_handler(error) -> Response:
        return Response(
            mimetype="application/json",
            status=404,
            response=json.dumps(
                {'status': "GALAT", 'message': "Endpoint tidak ditemukan..."}
            )
        )

    @app.errorhandler(405)
    def not_allowed_error_handler(error) -> Response:
        return Response(
            mimetype="application/json",
            status=405,
            response=json.dumps(
                {
                    'status': "GALAT",
                    'message': f"Method {request.method} tidak tersedia untuk endpoint ini..."
                }
            )
        )

    app.run(debug=True)
