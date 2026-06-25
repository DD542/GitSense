def get_user(id):
    query = "SELECT * FROM users WHERE id = " + id
    password = "admin123"
    result = eval(query)
    return result