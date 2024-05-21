import sqlite3
import bcrypt
from prettytable import PrettyTable
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Category, Style, Set, Product, OrderItem, SetItem, Role, User, SetOrder, Order
from sqlalchemy import inspect

database_path = 'db/database.db'

engine = create_engine('sqlite:///db/database.db')
Session = sessionmaker(bind=engine)
session = Session()


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
    cursor.execute(query, (username,))
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


def create_order(cart, user):
    if cart['products'] or cart['sets']:

        db = sqlite3.connect(database_path)
        cursor = db.cursor()
        cursor.execute("INSERT INTO orders (user_id) VALUES (?)", (user[0],))
        db.commit()

        cursor.execute("SELECT id FROM orders WHERE user_id = (?) ORDER BY id DESC LIMIT 1", (user[0],))
        order = cursor.fetchone()[0]

        total_price = 0
        data_products = []
        data_sets = []
        if cart['products']:
            for product in cart['products']:
                data = [product[2][0][0], order, product[3]]
                total_price += product[5]
                data_products.append(data)
        if cart['sets']:
            for set_one in cart['sets']:
                data = [set_one[2][0], order, set_one[3]]
                total_price += set_one[5]
                data_sets.append(data)
        cursor.executemany("INSERT INTO order_items (product_id, order_id, quantity) VALUES (?, ?, ?)", data_products)
        db.commit()

        cursor.executemany("INSERT INTO set_order (set_id, order_id, quantity) VALUES (?, ?, ?)", data_sets)
        db.commit()

        cursor.execute("UPDATE orders SET (total_price) = (?) WHERE id = (?) ", (total_price, order,))
        db.commit()

        db.close()
    else:
        print("Корзина пуста")


def main_menu(cart, user):
    while True:
        print("1. Посмотреть каталог")
        print("2. Посмотреть корзину")
        print("3. Выйти из аккаунта")
        choice = input("Enter your choice: ")
        if choice == "1":
            catalog_menu(cart)
        elif choice == "2":
            cart_table = PrettyTable()
            cart_table.field_names = ["id", "Тип продукта", "Корзина", "Количество", "Цена за штуку", "Цена"]
            n = 1
            for types in cart:
                for product in cart[types]:
                    product[0] = n
                    cart_table.add_row(product)
                    n += 1
            print(cart_table)
            while True:
                print("1. Оформление заказа")
                print("2. Удаление позиции из корзины")
                print("3. Изменение количества товара")
                print("4. Выход из меню")
                choice = input("Введите ваш выбор: ")
                if choice == "1":
                    create_order(cart, user)
                if choice == "2":
                    choice = input("Какую позицию вы хотите удалить?: ")
                    try:
                        choice = int(choice)
                    except ValueError:
                        print("Пожалуйста, введите правильное число.")
                        continue
                    for types in cart:
                        for product in cart[types]:
                            if product[0] == choice:
                                cart[types].remove(product)
                                print("Удаление успешно")

                if choice == "3":
                    choice = input("Какую позицию вы хотите изменить?: ")
                    try:
                        choice = int(choice)
                    except ValueError:
                        print("Пожалуйста, введите правильное число.")
                        continue
                    for types in cart:
                        n = 0
                        for product in cart[types]:
                            if product[0] == choice:
                                quantity = int(input("Новое значеение количества: "))
                                cart[types][n][3] = quantity
                                cart[types][n][5] = quantity * cart[types][n][4]
                                print("Изменение успешно")
                            n += 1

                if choice == "4":
                    break
        elif choice == "3":
            return None


def get_all_products_orm():
    products = session.query(Product).all()

    table = PrettyTable()
    table.field_names = ["ID", "Name", "Price", "Category", "Style"]

    rows = []
    for product in products:
        category_name = product.category.name if product.category else ""
        style_name = product.style.name if product.style else ""
        rows.append([product.id, product.name, product.price, category_name, style_name])

    table.add_rows(rows)

    print(table)


def add_product():
    name = input("Введите название товара: ")
    while True:
        try:
            price = float(input("Введите цену товара: "))
            break
        except ValueError:
            print("Ошибка: введите числовое значение для цены.")

    while True:
        try:
            category_id = int(input("Введите ID категории товара: "))
            # Проверка существования категории с указанным ID
            if session.query(Category).filter_by(id=category_id).count() == 0:
                print("Ошибка: категория с указанным ID не существует.")
                continue
            break
        except ValueError:
            print("Ошибка: введите целочисленное значение для ID категории.")

    while True:
        try:
            style_id = int(input("Введите ID стиля товара: "))
            # Проверка существования стиля с указанным ID
            if session.query(Style).filter_by(id=style_id).count() == 0:
                print("Ошибка: стиль с указанным ID не существует.")
                continue
            break
        except ValueError:
            print("Ошибка: введите целочисленное значение для ID стиля.")

    new_product = Product(name=name, price=price, category_id=category_id, style_id=style_id)
    session.add(new_product)
    session.commit()
    print(f"Добавлен новый товар: {name}")


def delete_product():
    while True:
        try:
            product_id = int(input("Введите ID товара для удаления: "))
            # Проверка существования товара с указанным ID
            if session.query(Product).filter_by(id=product_id).count() == 0:
                print("Ошибка: товар с указанным ID не существует.")
                continue
            break
        except ValueError:
            print("Ошибка: введите целочисленное значение для ID товара.")

    product = session.query(Product).filter_by(id=product_id).first()
    session.delete(product)
    session.commit()
    print(f"Товар с ID {product_id} удален")


def get_categories():
    categories = session.query(Category).all()
    table = PrettyTable()
    table.field_names = ["ID", "Name"]

    for category in categories:
        table.add_row([category.id, category.name])

    print(table)


def add_category():
    name = input("Введите название новой категории: ")

    new_category = Category(name=name)
    session.add(new_category)
    session.commit()
    print(f"Добавлена новая категория: {name}")

def delete_category():
    while True:
        try:
            category_id = int(input("Введите ID товара для удаления: "))
            # Проверка существования товара с указанным ID
            if session.query(Category).filter_by(id=category_id).count() == 0:
                print("Ошибка: товар с указанным ID не существует.")
                continue
            break
        except ValueError:
            print("Ошибка: введите целочисленное значение для ID товара.")

    category = session.query(Category).filter_by(id=category_id).first()
    session.delete(category)
    session.commit()
    print(f"Категория с ID {category_id} удалена")

def admin_menu():
    while True:
        print("1. Товары")
        print("2. Наборы")
        print("3. Заказы")
        print("4. Пользователи")
        print("5. Выйти из аккаунта")
        choice = input("Enter your choice: ")

        if choice == "1":
            product_menu()
        if choice == "2":
            pass
        if choice == "3":
            pass
        if choice == "5":
            return None


def product_menu():
    while True:
        print("1. Получить список товаров")
        print("2. Добавить товар")
        print("3. Удалить товар")
        print("4. Получить список категорий")
        print("5. Добавить категорию")
        print("6. Удалить категорию")
        print("7. Получить список стилей")
        print("8. Добавить стиль")
        print("9. Удалить стиль")
        print("0. Назад")
        choice = input("Введите ваш выбор: ")

        if choice == "1":
            print(get_all_products_orm())
        elif choice == "2":
            add_product()
        elif choice == "3":
            delete_product()
        elif choice == "4":
            get_categories()
        elif choice == "5":
            add_category()
        elif choice == "6":
            delete_category()
        elif choice == "7":
            get_styles()
        elif choice == "8":
            add_styles()
        elif choice == "9":
            delete_style()
        elif choice == "0":
            return None
        else:
            print("Неверный выбор. Пожалуйста, выберите снова.")


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
            return user
    elif choice == "2":
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        name = input("Enter your name: ")
        role_id = 2
        user = register(username, password, name, role_id)
        if user:
            return user
    elif choice == "3":
        print("Exiting the program")
        raise SystemExit(1)


def catalog_menu(cart):
    while True:
        print("Catalog Menu")
        print("1. View all products")
        print("2. View all sets")
        print("3. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            products = get_all_products()
            product_table = PrettyTable()
            product_table.field_names = ["ID", "Название", "Цена", "Категория", "Стиль"]
            product_table.add_rows(products)
            print(product_table)
            while True:
                choice = input(
                    "Для добавления товара в корзину введите его ID, для выхода из меню нажмите 0, для отображения списка продуктов нажмите 00: ")
                if choice == "0":
                    return False
                elif choice == "00":
                    print(product_table)
                    continue
                try:
                    choice = int(choice)
                except ValueError:
                    print("Пожалуйста, введите правильное число.")
                    continue
                product = ["1", "Продукт", get_product(choice)]

                if product:
                    quantity = input("Введите количество товара: ")
                    try:
                        quantity = int(quantity)
                    except ValueError:
                        print("Пожалуйста, введите правильное число.")
                        continue
                    product.append(quantity)
                    product.append(product[2][0][2])
                    product.append(product[2][0][2] * quantity)
                    cart['products'].append(product)
                    print(f'Продукт {product[2][0][1]} в количестве {quantity} успешно добавлен в корзину')
                else:
                    print("Продукта с таким ID не найдено")

        if choice == "2":
            sets = get_all_sets()
            table = PrettyTable()
            table.field_names = ["ID", "Название", "Скидка %", "Старая цена", "Новая цена"]
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
                    table_set.field_names = ["ID продукта", "Название продукта", "Количеество", "Старая цена",
                                             "Новая цена", "Категория", "Стиль"]
                    table_set.add_rows(set_one)
                    print(table_set)
                    quantity = input("Введите количство наборов которое хотите добавить в корзину или нажмите 0 для "
                                     "выхода из меню: ")
                    if quantity == "0":
                        continue
                    try:
                        quantity = int(quantity)
                    except ValueError:
                        print("Пожалуйста, введите правильное число.")
                        continue
                    set_table = ["1", "Набор", sets[choice - 1], quantity, sets[choice - 1][4],
                                 sets[choice - 1][4] * quantity]
                    cart['sets'].append(set_table)
                    print(f'Набор {sets[choice - 1]} в количестве {quantity} успешно добавлен в корзину')
                else:
                    print("Набор с таким id не найден.")
        if choice == "3":
            return False


def get_all_products():
    db = sqlite3.connect(database_path)
    cursor = db.cursor()

    query = """
            SELECT p.id, p.name, price, c.name, s.name FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            LEFT JOIN style s on s.id = p.style_id
            """
    cursor.execute(query)
    products = cursor.fetchall()

    db.close()

    return products


def get_product(id):
    db = sqlite3.connect(database_path)
    cursor = db.cursor()

    query = """
            SELECT p.id, p.name, price, c.name, s.name FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            LEFT JOIN style s on s.id = p.style_id
            WHERE p.id == ?
            """
    cursor.execute(query, (id,))
    product = cursor.fetchall()

    db.close()

    return product


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
    user = None
    cart = {'products': [],
            'sets': []}
    while True:
        # Блок меню авторизации
        if user_role_id is None:
            user = auth_menu()
            if user:
                user_role_id = user[4]
                cart = {'products': [],
                        'sets': []}
        # Блок основного меню
        if user_role_id == 1:
            user_role_id = main_menu(cart, user)
        elif user_role_id == 2:
            user_role_id = admin_menu()


if __name__ == "__main__":
    main()
