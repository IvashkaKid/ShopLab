import unittest
import sqlite3
from main import get_product

class TestGetProductFunction(unittest.TestCase):
    def test_get_product(self):
        product = get_product(1)
        self.assertEqual(product[0][1], "Стул ДЕКО")  # Первый элемент кортежа содержит имя продукта
        self.assertEqual(product[0][2], 100.0)  # Второй элемент кортежа содержит цену продукта
        self.assertEqual(product[0][3], "Деревянная мебель")  # Третий элемент кортежа содержит ID категории
        self.assertEqual(product[0][4], "Модерн")  # Четвертый элемент кортежа содержит ID стиля

    def test_get_nonexistent_product(self):
        product = get_product(1000)
        expected = None
        self.assertEqual(product, None)

    def test_invalid_input(self):
        product = get_product("Текст, а не id")
        self.assertEqual(get_product(product), None)


if __name__ == '__main__':
    unittest.main()
