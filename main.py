import enum
import uuid
from typing import List, Optional

CURRENT_TIME = 0  # current time in months


class UserStatusSavingEnum(enum.Enum, str):
    UNPAID_LOANS = "UNPAID_LOANS"  # start draining savings account
    LOCKED = "LOCKED"
    ACTIVE = "ACTIVE"


class Loan:
    sum: int
    initiated_at: int

    def __init__(self, sum: int, initiated_at: int):
        if sum > 10_000:
            raise ValueError("Bank do not give loans more than $10000")
        self.sum = sum
        self.initiated_at = initiated_at


class User:
    id: uuid.UUID
    loans: List[Loan]
    saving: int
    status: UserStatusSavingEnum

    def __init__(self, loans: Optional[Loan] = None, saving: int = 0):
        self.id = uuid.UUID()
        self.loans = loans or []
        self.saving = saving
        self.status = UserStatusSavingEnum.ACTIVE

    def add_loan(self, loan: Loan):
        if self.status == UserStatusSavingEnum.LOCKED:
            raise ValueError("User is locked")
        if self.status == UserStatusSavingEnum.UNPAID_LOANS:
            raise ValueError("User has unpaid loans")
        if len(self.loans) > 3:
            raise ValueError("User can not have more than 3 loans concurrently")
        self.loans.append(loan)

    def withdraw_savings(self, amount):
        if self.status == UserStatusSavingEnum.LOCKED:
            raise ValueError("User is locked")
        if self.status == UserStatusSavingEnum.UNPAID_LOANS:
            raise ValueError("User has unpaid loans")
        if amount > self.saving:
            raise ValueError("Not enough money in savings account")
        self.saving -= amount
        print(f"Withdrawn ${amount} from savings account. Current savings: ${self.saving}")

    def deposit_savings(self, amount):
        if self.status == UserStatusSavingEnum.LOCKED:
            raise ValueError("User is locked")
        self.saving += amount
