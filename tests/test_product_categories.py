"""
Тесты для классов Product и Category
"""

import pytest
from src.product_categories import Product, Category


class TestProduct:
    """Тесты для класса Product"""

    def test_product_initialization(self):
        """Тест корректной инициализации продукта"""
        product = Product("Телефон", "Смартфон", 50000.0, 10)

        assert product.name == "Телефон"
        assert product.description == "Смартфон"
        assert product.price == 50000.0
        assert product.quantity == 10

    def test_product_initialization_with_float_price(self):
        """Тест инициализации с ценой в виде float"""
        product = Product("Ноутбук", "Игровой ноутбук", 89999.99, 5)

        assert isinstance(product.price, float)
        assert product.price == 89999.99

    def test_product_initialization_with_int_quantity(self):
        """Тест инициализации с количеством в виде int"""
        product = Product("Наушники", "Беспроводные", 5000.0, 100)

        assert isinstance(product.quantity, int)
        assert product.quantity == 100


class TestCategory:
    """Тесты для класса Category"""

    def test_category_initialization_without_products(self):
        """Тест инициализации категории без товаров"""
        category = Category("Электроника", "Электронные товары")

        assert category.name == "Электроника"
        assert category.description == "Электронные товары"
        assert category.products == []

    def test_category_initialization_with_products(self):
        """Тест инициализации категории с товарами"""
        product1 = Product("Телефон", "Смартфон", 50000.0, 10)
        product2 = Product("Ноутбук", "Игровой", 80000.0, 5)

        category = Category("Электроника", "Электронные товары", [product1, product2])

        assert category.name == "Электроника"
        assert len(category.products) == 2
        assert category.products[0].name == "Телефон"
        assert category.products[1].name == "Ноутбук"

    def test_category_count_increments(self):
        """Тест увеличения счётчика категорий"""
        initial_count = Category.category_count

        category1 = Category("Категория1", "Описание1")
        category2 = Category("Категория2", "Описание2")

        assert Category.category_count == initial_count + 2

    def test_product_count_increments(self):
        """Тест увеличения счётчика товаров"""
        initial_count = Category.product_count

        product1 = Product("Товар1", "Описание1", 100.0, 10)
        product2 = Product("Товар2", "Описание2", 200.0, 5)

        category = Category("Категория", "Описание", [product1, product2])

        assert Category.product_count == initial_count + 2

    def test_product_count_increments_with_empty_category(self):
        """Тест увеличения счётчика товаров при пустой категории"""
        initial_count = Category.product_count

        category = Category("Пустая категория", "Описание")

        assert Category.product_count == initial_count


class TestIntegration:
    """Интеграционные тесты"""

    def test_category_and_product_integration(self):
        """Тест совместной работы Category и Product"""
        product1 = Product("Товар A", "Описание A", 1000.0, 3)
        product2 = Product("Товар B", "Описание B", 2000.0, 7)

        category = Category("Тестовая категория", "Тестовое описание", [product1, product2])

        assert len(category.products) == 2
        assert category.products[0].price == 1000.0
        assert category.products[1].price == 2000.0
