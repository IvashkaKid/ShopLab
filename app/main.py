import sqlite3
import bcrypt
from prettytable import PrettyTable

database_path = 'db/database.db'


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def check_password(password, hash_password):
    return bcrypt.checkpw(password.encode('utf-8'), hash_password.encode('utf-8'))


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
        password = hash_password(password)
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
    query = """SELECT * FROM users WHERE username=?"""
    cursor.execute(query, (username, ))
    user = cursor.fetchone()

    db.close()

    if user:
        saved_password = user[3]
        if check_password(password, saved_password):
            print("Вы вошли успешно")
            return user
        else:
            print("Неправильный логин или пароль")
            return None
    else:
        print("Неправильный логин или пароль")
        return None

def main_menu():
    while True:
        print("1. Посмотреть каталог")
        print("2. Посмотреть корзину")
        print("3. Оформить заказ")
        print("4. Выйти из аккаунта")
        choice = input("Enter your choice: ")
        if choice == "1":
            catalog_menu()
        if choice == "4":
            return None


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
        raise SystemExit(1)


def catalog_menu():
    while True:
        print("Catalog Menu")
        print("1. View all products")
        print("2. View all sets")
        print("3. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            products = get_all_products()
            for product in products:
                print(product)
        if choice == "2":
            sets = get_all_sets()
            table = PrettyTable()
            table.field_names = ["ID", "Название", "Скидка %", "Старая цена","Новая цена"]
            table.add_rows(sets)

            print(table)
            while True:
                print("Введите id набора для его просмотра, 0 для выхода в меню, 00 для отображения всех наборов")
                choice = (input("Хотите посмотреть какой-нибудь набор?: "))
                if choice == "0":
                    return False
                if choice == "00":
                    print(table)
                    continue

                try:
                    choice = int(choice)
                except ValueError:
                    print("Пожалуйста, введите правильное число.")
                    continue

                set_one = get_set(choice)

                if set_one:
                    table_set = PrettyTable()
                    table_set.field_names = ["ID продукта", "Название продукта","Количеество", "Старая цена", "Новая цена", "Категория", "Стиль"]
                    table_set.add_rows(set_one)
                    print(table_set)
                else:
                    print("Набор с таким id не найден.")
        if choice == "3":
            return False


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

    query = """
            SELECT s.id, s.name,s.discount, SUM(p.price) AS old_price,
            SUM( p.price - (p.price * (s.discount/100.0))) AS new_price
            FROM sets s 
            LEFT JOIN set_items si ON s.id = si.set_id 
            LEFT JOIN products p ON si.product_id = p.id 
            GROUP BY set_id
            """
    cursor.execute(query)
    sets = cursor.fetchall()

    db.close()

    return sets


def get_set(id):
    db = sqlite3.connect(database_path)
    cursor = db.cursor()

    query = """SELECT p.id AS product_id, p.name AS product, si.quantity,p.price * si.quantity AS old_price, 
    p.price * si.quantity - (p.price * si.quantity * (s.discount / 100.0)) AS new_price , c.name AS category, 
    st.name AS style 
    FROM sets s 
    LEFT JOIN set_items si ON s.id = si.set_id 
    LEFT JOIN products p ON si.product_id = p.id 
    LEFT JOIN categories c ON c.id = p.category_id 
    LEFT JOIN style st ON st.id = p.style_id 
    WHERE s.id == ?"""
    cursor.execute(query, (id,))
    set_one = cursor.fetchall()

    db.close()

    return set_one

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
