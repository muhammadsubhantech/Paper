# Task 06 - Banking Ledger with OOP

from dataclasses import dataclass
from itertools import count


transaction_numbers = count(1)


@dataclass(frozen=True)
class Transaction:
    transaction_id: int
    action: str
    amount: float
    balance: float


class Account:
    def __init__(self, account_number, opening_balance=0):
        if opening_balance < 0:
            raise ValueError("Opening balance cannot be negative")

        self.account_number = account_number
        self.__balance = opening_balance
        self.__transactions = []

    @property
    def balance(self):
        return self.__balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")

        self.__balance += amount
        record = Transaction(next(transaction_numbers), "deposit",
                             amount, self.__balance)
        self.__transactions.append(record)

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self.__balance:
            raise ValueError("Insufficient funds")

        self.__balance -= amount
        record = Transaction(next(transaction_numbers), "withdraw",
                             amount, self.__balance)
        self.__transactions.append(record)

    def statement(self):
        # A tuple prevents the caller from changing the stored records.
        return tuple(self.__transactions)


class Bank:
    def __init__(self):
        self.accounts = {}

    def add_account(self, account):
        if account.account_number in self.accounts:
            raise ValueError("Account already exists")
        self.accounts[account.account_number] = account

    def get_account(self, account_number):
        if account_number not in self.accounts:
            raise ValueError("Account does not exist")
        return self.accounts[account_number]

    def transfer(self, from_number, to_number, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if from_number == to_number:
            raise ValueError("Use two different accounts")

        sender = self.get_account(from_number)
        receiver = self.get_account(to_number)

        if sender.balance < amount:
            raise ValueError("Insufficient funds")

        # Both accounts are checked before either balance is changed.
        sender._Account__balance -= amount
        receiver._Account__balance += amount

        sender._Account__transactions.append(
            Transaction(next(transaction_numbers), "transfer out",
                        amount, sender.balance)
        )
        receiver._Account__transactions.append(
            Transaction(next(transaction_numbers), "transfer in",
                        amount, receiver.balance)
        )


if __name__ == "__main__":
    bank = Bank()
    bank.add_account(Account("A", 1000))
    bank.add_account(Account("B", 200))

    bank.transfer("A", "B", 350)

    print("A balance:", bank.get_account("A").balance)
    print("B balance:", bank.get_account("B").balance)
    print("A statement:", bank.get_account("A").statement())
