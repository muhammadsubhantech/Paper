# Task 10 - CSV Inventory Reconciliation

import csv


def update_inventory(inventory_file, movements_file):
    stock = {}

    # Read current stock.
    with open(inventory_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            sku = row["sku"]
            quantity = int(row["quantity"])

            if quantity < 0:
                raise ValueError("Inventory quantity cannot be negative")
            if sku in stock:
                raise ValueError("Duplicate SKU: " + sku)

            stock[sku] = {"name": row["name"], "quantity": quantity}

    rejected = []

    # Process movements in their file order.
    with open(movements_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            sku = row["sku"]
            movement_type = row["type"].strip().upper()

            try:
                units = int(row["units"])
            except (ValueError, TypeError):
                rejected.append({**row, "reason": "Units must be a whole number"})
                continue

            if sku not in stock:
                reason = "Unknown SKU"
            elif units <= 0:
                reason = "Units must be greater than zero"
            elif movement_type not in ("IN", "OUT"):
                reason = "Movement type must be IN or OUT"
            elif movement_type == "OUT" and stock[sku]["quantity"] < units:
                reason = "Not enough stock"
            else:
                reason = ""

            if reason:
                rejected.append({**row, "reason": reason})
                continue

            if movement_type == "IN":
                stock[sku]["quantity"] += units
            else:
                stock[sku]["quantity"] -= units

    # Save updated stock.
    with open("updated_inventory.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["sku", "name", "quantity"])

        for sku, details in stock.items():
            writer.writerow([sku, details["name"], details["quantity"]])

    # Save rejected movements and their reasons.
    with open("rejected_movements.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=["sku", "type", "units", "reason"]
        )
        writer.writeheader()
        writer.writerows(rejected)

    return stock, rejected


if __name__ == "__main__":
    final_stock, rejected_rows = update_inventory(
        "inventory.csv", "movements.csv"
    )
    print("Final inventory:", final_stock)
    print("Rejected movements:", rejected_rows)
