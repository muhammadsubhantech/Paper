# Task 07 - Employee Payroll Engine

from abc import ABC, abstractmethod


class Employee(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def calculate_pay(self):
        pass


class SalariedEmployee(Employee):
    def __init__(self, name, monthly_salary):
        super().__init__(name)
        self.monthly_salary = monthly_salary

    def calculate_pay(self):
        return self.monthly_salary


class HourlyEmployee(Employee):
    def __init__(self, name, hourly_rate, hours):
        super().__init__(name)
        self.hourly_rate = hourly_rate
        self.hours = hours

    def calculate_pay(self):
        if self.hours <= 40:
            return self.hourly_rate * self.hours

        normal_pay = 40 * self.hourly_rate
        overtime_pay = (self.hours - 40) * self.hourly_rate * 1.5
        return normal_pay + overtime_pay


class CommissionEmployee(Employee):
    def __init__(self, name, base_salary, sales, rate):
        super().__init__(name)
        self.base_salary = base_salary
        self.sales = sales
        self.rate = rate

    def calculate_pay(self):
        return self.base_salary + self.sales * self.rate


def payroll_summary(employees):
    summary = []

    for employee in employees:
        summary.append({
            "name": employee.name,
            "pay": employee.calculate_pay()
        })

    return summary


if __name__ == "__main__":
    staff = [
        HourlyEmployee("Ali", 20, 45),
        CommissionEmployee("Sara", 500, 4000, 0.10),
        SalariedEmployee("Ahmed", 3000)
    ]

    for person in payroll_summary(staff):
        print(person)
