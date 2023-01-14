from mysql.connector.connection import MySQLCursor


def empty_or_rows(cursor: MySQLCursor):
    data = []

    try:
        rows = cursor.fetchall()
    except IndexError:
        return []

    for row in rows:
        data.append(row)

    return rows


def empty_or_row(cursor: MySQLCursor):
    try:
        row = cursor.fetchall()[0]
    except IndexError:
        return []

    return [column for column in row]
