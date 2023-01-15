from mysql.connector.connection import MySQLCursorDict


def empty_or_rows(cursor: MySQLCursorDict):
    data = []

    try:
        rows = cursor.fetchall()
    except IndexError:
        return []

    for row in rows:
        data.append(row)

    return data


def empty_or_row(cursor: MySQLCursorDict):
    try:
        row = cursor.fetchall()[0]
    except IndexError:
        return {}

    return row
