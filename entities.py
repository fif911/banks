import enum
import random
from typing import List, Optional

from faker import Faker


class Session:
    current_time: int  # current time in months
    users: List["User"]
    faker: Faker

    def __init__(self):
        self.users = []
        self.current_time = 0
        self.faker = Faker()

    def populate_db(self):
        for _ in range(10):
            user = User(self, saving=random.randint(0, 50_000))
            for _ in range(random.randint(0, 3)):
                user.add_loan(Loan(random.randint(0, 10_000), self.current_time))
            self.users.append(user)


class UserStatusSavingEnum(str, enum.Enum):
    OVERDUE_LOANS = "OVERDUE_LOANS"  # start draining savings account
    LOCKED = "LOCKED"
    ACTIVE = "ACTIVE"


class Loan:
    sum: int
    initiated_at: int
    interest_rate: float

    def __init__(self, amount: int, initiated_at: int):
        if amount <= 0:
            raise ValueError("Loan amount can not be negative or zero")
        if amount > 10_000:
            raise ValueError("Bank do not give loans more than €10000")

        self.sum = amount
        self.initiated_at = initiated_at
        if amount >= 2_000:
            self.interest_rate = 0.105  # 10.5%
        else:
            self.interest_rate = 0.1  # 10%

    def is_expired(self, session: Session) -> bool:
        """
        If a loan is not paid within 12 months after initiating the loan,
        the savings account will be drained and locked until the loan is
        paid in full.
        """
        return self.initiated_at + 12 <= session.current_time

    @staticmethod
    def issue_loan(amount, ) -> "Loan":
        pass

    def __repr__(self):
        return f"Loan(sum={self.sum}, initiated_at={self.initiated_at}, interest_rate={self.interest_rate})"


class User:
    username: str
    full_name: str
    loans: List[Loan]
    saving: int
    status: UserStatusSavingEnum

    def __init__(self, session: Session, loans: Optional[Loan] = None, saving: int = 0):
        self.full_name = session.faker.unique.first_name() + " " + session.faker.unique.last_name()
        self.username = self.full_name.lower().replace(" ", "_")
        self.loans = loans or []
        self.saving = saving
        self.saving_interest_rate = 0.05 if saving >= 100_000 else 0.055
        self.status = UserStatusSavingEnum.ACTIVE

    def add_loan(self, loan: Loan):
        if self.status == UserStatusSavingEnum.LOCKED:
            raise ValueError("User is locked")
        if self.status == UserStatusSavingEnum.OVERDUE_LOANS:
            raise ValueError("User has unpaid loans")
        if len(self.loans) > 3:
            raise ValueError("User can not have more than 3 loans concurrently")
        self.loans.append(loan)

    def withdraw_savings(self, amount):
        if self.status == UserStatusSavingEnum.LOCKED:
            raise ValueError("User is locked")
        if self.status == UserStatusSavingEnum.OVERDUE_LOANS:
            raise ValueError("User has unpaid loans")
        if amount > self.saving:
            raise ValueError("Not enough money in savings account")
        self.saving -= amount
        print(f"Withdrawn €{amount} from savings account. Current savings: ${self.saving}")

    def deposit_savings(self, amount):
        if self.status == UserStatusSavingEnum.LOCKED:
            raise ValueError("User is locked")
        self.saving += amount

    def __repr__(self):
        return f"User(username={self.username}, full_name={self.full_name}, loans={self.loans}, saving=€{self.saving}, status={self.status})"
