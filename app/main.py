import sqlite3

database_path = 'db/database.db'


def register(username, password, name, role_id):
    db = sqlite3.connect(database_path)
    cursor = db.cursor()

    query = """SELECT * FROM users WHERE username=?"""
    cursor.execute(query, (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        print("Пользователь с таким логином уже зарегистрирован")
        return

    query = "INSERT INTO users (username, password, name, role_id) VALUES (?, ?, ?, ?)"
    try:
        cursor.execute(query, (username, password, name, role_id))
        db.commit()
        print("Регистрация успешна")
        db.close()
        return existing_user
    except sqlite3.Error as e:
        print("Ошибка при работе с базой данных:", e)


def auth(username, password):
    db = sqlite3.connect(database_path)
    cursor = db.cursor()

    query = """SELECT * FROM users WHERE username=? AND password=?"""
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    db.close()

    if user:
        print("Вы вошли успешно")
        return user
    else:
        print("Неправильный логин или пароль")


def main_menu():
    while True:
        print("1. Посмотреть каталог")
        print("2. Посмотреть корзину")
        print("3. Оформить заказ")
        print("4. Выйти из аккаунта")
        choice = input("Enter your choice: ")
        if choice == 1:
            catalog_menu()
        if choice == 4:
            return None
        break


def admin_menu():
    pass


def auth_menu():
    print("Welcome to the Console Authentication System")
    print("1. Login")
    print("2. Register")
    print("3. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        user = auth(username, password)
        if user:
            return user[4]
    elif choice == "2":
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        name = input("Enter your name: ")
        role_id = 1
        user = register(username, password, name, role_id)
        if user:
            return user[4]
    elif choice == "3":
        print("Exiting the program")
        return False



def catalog_menu():
    print("Catalog Menu")
    print("1. View all products")
    print("2. View all sets")
    print("3. Exit")

    choice = input("Enter your choice: ")
    return choice


def get_all_products():
    db = sqlite3.connect(database_path)
    cursor = db.cursor()

    query = "SELECT * FROM products"
    cursor.execute(query)
    products = cursor.fetchall()

    db.close()

    return products


def get_all_sets():
    db = sqlite3.connect(database_path)
    cursor = db.cursor()

    query = "SELECT * FROM sets"
    cursor.execute(query)
    sets = cursor.fetchall()

    db.close()

    return sets


def main():
    user_role_id = None
    while True:
        # Блок меню авторизации
        if user_role_id is None:
            user_role_id = auth_menu()
        # Блок основного меню
        if user_role_id == 1:
            user_role_id = main_menu()
        elif user_role_id == 2:
            user_role_id = admin_menu()




if __name__ == "__main__":
    main()
