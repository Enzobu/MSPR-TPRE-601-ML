def read_sql_query(filename):
    with open(filename, 'r') as file:
        query = file.read()
    return query
