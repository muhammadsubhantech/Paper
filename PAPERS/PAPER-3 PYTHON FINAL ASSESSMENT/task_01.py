# Task 01 - Nested Transaction Analyzer

def analyze_transactions(transactions, customers=None):
    totals = {}
    categories = {}
    used_ids = set()

    # Add customers first, including customers with no successful spending.
    if customers:
        for name in customers:
            totals[name] = 0
            categories[name] = {}

    for transaction in transactions:
        transaction_id = transaction["id"]

        if transaction_id in used_ids:
            raise ValueError("Duplicate transaction ID: " + str(transaction_id))
        used_ids.add(transaction_id)

        name = transaction["customer"]

        if name not in totals:
            totals[name] = 0
            categories[name] = {}

        if transaction["status"].lower() != "success":
            continue

        amount = transaction["amount"]
        category = transaction["category"]

        if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount < 0:
            raise ValueError("Transaction amount must be a non-negative number")

        totals[name] += amount

        if category not in categories[name]:
            categories[name][category] = 0
        categories[name][category] += amount

    report = []

    for name in totals:
        top_category = None

        for category in categories[name]:
            if top_category is None:
                top_category = category
            elif categories[name][category] > categories[name][top_category]:
                top_category = category
            elif categories[name][category] == categories[name][top_category]:
                if category < top_category:
                    top_category = category

        report.append({
            "customer": name,
            "total_spending": totals[name],
            "top_category": top_category
        })

    report.sort(key=lambda item: (-item["total_spending"], item["customer"]))

    for number in range(len(report)):
        report[number]["rank"] = number + 1

    return report


if __name__ == "__main__":
    transactions = [
        {"id": 1, "customer": "Ali", "category": "Food",
         "amount": 500, "status": "success"},
        {"id": 2, "customer": "Ali", "category": "Travel",
         "amount": 200, "status": "failed"},
        {"id": 3, "customer": "Sara", "category": "Food",
         "amount": 700, "status": "success"},
        {"id": 4, "customer": "Ahmed", "category": "Shopping",
         "amount": 100, "status": "failed"}
    ]

    print(analyze_transactions(transactions))
