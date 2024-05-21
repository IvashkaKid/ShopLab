import unittest
from main import get_product

class TestGetProductFunction(unittest.TestCase):
    def test_get_product(self):
        product = get_product(1)
        self.assertEqual(product[0][1], "Стул ДЕКО")
        self.assertEqual(product[0][2], 100.0)
        self.assertEqual(product[0][3], "Деревянная мебель")
        self.assertEqual(product[0][4], "Модерн")

    def test_get_nonexistent_product(self):
        product = get_product(1000)
        self.assertEqual(product, None)

    def test_invalid_input(self):
        product = get_product("Текст, а не id")
        self.assertEqual(get_product(product), None)


if __name__ == '__main__':
    unittest.main()
