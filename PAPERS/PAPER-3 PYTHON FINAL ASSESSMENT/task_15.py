# Task 15 - Integrated Order Fulfillment System

import json
import os
import uuid
import unittest


class Product:
    def __init__(self, product_id, name, price, stock):
        if price < 0 or stock < 0:
            raise ValueError("Price and stock cannot be negative")

        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock


class Cart:
    def __init__(self):
        self.items = {}

    def add_product(self, product_id, quantity):
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            raise ValueError("Quantity must be a positive whole number")

        if product_id not in self.items:
            self.items[product_id] = 0

        self.items[product_id] += quantity


class Order:
    def __init__(self, items, total):
        self.order_id = str(uuid.uuid4())
        self.items = items
        self.total = total


class Inventory:
    def __init__(self, products):
        self.products = {}

        for product in products:
            if product.product_id in self.products:
                raise ValueError("Duplicate product ID")
            self.products[product.product_id] = product

    @classmethod
    def from_json(cls, path):
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        products = []
        for item in data:
            products.append(Product(
                item["product_id"], item["name"],
                item["price"], item["stock"]
            ))

        return cls(products)

    def place_order(self, cart, discount, orders_file="orders.json"):
        if not isinstance(discount, (int, float)) or discount < 0 or discount > 100:
            raise ValueError("Discount must be from 0 to 100")

        # Check every cart item before changing any stock.
        total = 0
        order_items = []

        for product_id, quantity in cart.items.items():
            if quantity <= 0:
                raise ValueError("Quantity must be positive")

            if product_id not in self.products:
                raise ValueError("Product does not exist")

            product = self.products[product_id]

            if quantity > product.stock:
                raise ValueError("Not enough stock for " + product.name)

            total += product.price * quantity
            order_items.append({
                "product_id": product_id,
                "quantity": quantity,
                "price": product.price
            })

        total = total - (total * discount / 100)
        order = Order(order_items, total)

        # Remember old stock so it can be restored if saving fails.
        old_stock = {}
        for product_id, quantity in cart.items.items():
            old_stock[product_id] = self.products[product_id].stock

        try:
            for product_id, quantity in cart.items.items():
                self.products[product_id].stock -= quantity

            # Read old orders, then safely replace the file.
            if os.path.exists(orders_file):
                with open(orders_file, "r", encoding="utf-8") as file:
                    saved_orders = json.load(file)
            else:
                saved_orders = []

            saved_orders.append({
                "order_id": order.order_id,
                "items": order.items,
                "total": order.total
            })

            temporary_file = orders_file + ".tmp"
            with open(temporary_file, "w", encoding="utf-8") as file:
                json.dump(saved_orders, file, indent=4)

            os.replace(temporary_file, orders_file)

        except Exception:
            for product_id, old_quantity in old_stock.items():
                self.products[product_id].stock = old_quantity
            raise

        return order


# Three basic unit tests
class OrderTests(unittest.TestCase):
    def setUp(self):
        self.inventory = Inventory([Product("P1", "Pen", 100, 5)])
        self.cart = Cart()

    def test_successful_order_and_discount(self):
        self.cart.add_product("P1", 2)
        order = self.inventory.place_order(self.cart, 10, "test_orders.json")
        self.assertEqual(order.total, 180)
        self.assertEqual(self.inventory.products["P1"].stock, 3)
        if os.path.exists("test_orders.json"):
            os.remove("test_orders.json")

    def test_rejects_out_of_stock(self):
        self.cart.add_product("P1", 6)
        with self.assertRaises(ValueError):
            self.inventory.place_order(self.cart, 0, "test_orders.json")
        self.assertEqual(self.inventory.products["P1"].stock, 5)

    def test_rejects_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.cart.add_product("P1", 0)


if __name__ == "__main__":
    # Run tests with: python task_15.py
    unittest.main()
