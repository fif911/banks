import enum
import random
from typing import List, Optional

from faker import Faker

from utils import IOUtils


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
    OVERDUE_LOANS = "OVERDUE_LOANS"  # user has not paid a loan within 12 month - start draining savings account
    LOCKED = "LOCKED"  # user cannot perform any actions except for logging out
    ACTIVE = "ACTIVE"  # default status


class LoanStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAID = "PAID"


class Loan:
    """Loan entity

    Is issued for 12 months. After 12 months, the loan is expired.
    Each user may have up to 3 loans.
    Each loan has an interest rate of 10% for loans up to €2000 and 10.5% for loans equal or above €2000.
    The loan is represented as a float number with max 2 decimal places, and is rounded to the nearest cent if needed.
    """
    sum: float
    initiated_at: int
    interest_rate: float
    status: LoanStatusEnum

    def __init__(self, amount: float, initiated_at: int):
        if amount <= 0:
            raise ValueError("Loan amount can not be negative or zero")
        if amount > 10_000:
            raise ValueError("Bank do not give loans more than €10000")

        self.sum = IOUtils.round_float_to_2_decimal_places(amount)
        self.initiated_at = initiated_at
        if amount >= 2_000:
            self.interest_rate = 0.105  # 10.5%
        else:
            self.interest_rate = 0.1  # 10%
        self.status = LoanStatusEnum.ACTIVE

    def is_expired(self, session: Session) -> bool:
        """
        If a loan is not paid within 12 months after initiating the loan,
        the savings account will be drained and locked until the loan is
        paid in full.
        """
        return self.initiated_at + 12 <= session.current_time

    def expires_in(self, session: Session) -> int:
        """Returns the number of months until the loan expires"""
        expires_in = self.initiated_at + 12 - session.current_time
        return expires_in if expires_in > 0 else 0

    def pay(self, amount: float) -> LoanStatusEnum:
        """Allow user to pay for a loan and returns the loan status"""
        amount = IOUtils.round_float_to_2_decimal_places(amount)
        if not amount > 0:
            raise ValueError("Payment amount can not be negative or zero")
        self.sum -= amount

        if self.sum <= 0:
            self.sum = 0
            self.status = LoanStatusEnum.PAID
            print("Loan is paid in full and is closed. Thank you!")

        return self.status

    def pretty_print_loan(self, session: Session, prefix: str = ""):
        loan_print = prefix + f"Loan: €{self.sum}, initiated at: {self.initiated_at}, " \
                              f"interest_rate {self.interest_rate}, expired: {self.is_expired(session)}"
        # add the expiration date if the loan is not expired
        loan_print = loan_print + f", expires in: {self.expires_in(session)}" \
            if self.is_expired(session) is False else loan_print
        print(loan_print)

    @staticmethod
    def issue_loan(session: Session, loan_amount: float):
        """Loan factory method"""
        return Loan(loan_amount, session.current_time)

    def __repr__(self):
        return f"Loan(sum={self.sum}, initiated_at={self.initiated_at}, interest_rate={self.interest_rate})"


class User:
    username: str
    full_name: str
    loans: List[Loan]
    saving: float
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

    def withdraw_savings(self, amount: float):
        if self.status == UserStatusSavingEnum.LOCKED:
            raise ValueError("User is locked")
        if self.status == UserStatusSavingEnum.OVERDUE_LOANS:
            raise ValueError("User has unpaid loans")
        if amount > self.saving:
            raise ValueError("Not enough money in savings account")
        self.saving -= amount
        print(f"Withdrawn €{amount} from savings account. Current savings: ${self.saving}")

    def deposit_savings(self, deposit_amount: float):
        if self.status == UserStatusSavingEnum.LOCKED:
            raise ValueError("User is locked")
        self.saving += deposit_amount
        print(f"Deposited €{deposit_amount}. Current savings: €{self.saving}")

    def __repr__(self):
        return f"User(username={self.username}, full_name={self.full_name}, loans={self.loans}, " \
               f"saving=€{self.saving}, status={self.status})"
