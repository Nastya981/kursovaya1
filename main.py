"""
Главный модуль для демонстрации работы классов Product и Category
"""

from src.product_categories import Product, Category


def main() -> None:
    """Основная функция для демонстрации работы классов"""
    print("=" * 50)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ КЛАССОВ Product И Category")
    print("=" * 50)

    # Создаём товары
    product1 = Product("Смартфон", "Мощный смартфон с отличной камерой", 50000.0, 15)
    product2 = Product("Ноутбук", "Игровой ноутбук с высокой производительностью", 89999.99, 8)
    product3 = Product("Наушники", "Беспроводные наушники с шумоподавлением", 5000.0, 30)

    print("\n📦 Товары:")
    print(f"  - {product1.name}: {product1.description} - {product1.price} руб. (в наличии: {product1.quantity} шт.)")
    print(f"  - {product2.name}: {product2.description} - {product2.price} руб. (в наличии: {product2.quantity} шт.)")
    print(f"  - {product3.name}: {product3.description} - {product3.price} руб. (в наличии: {product3.quantity} шт.)")

    # Создаём категории
    electronics = Category("Электроника", "Электронные товары и гаджеты", [product1, product2])
    audio = Category("Аудио", "Аудио-товары", [product3])

    print("\n📂 Категории:")
    print(f"  - {electronics.name}: {electronics.description} (товаров: {len(electronics.products)})")
    print(f"  - {audio.name}: {audio.description} (товаров: {len(audio.products)})")

    print("\n📊 Статистика:")
    print(f"  - Всего категорий: {Category.category_count}")
    print(f"  - Всего товаров: {Category.product_count}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
