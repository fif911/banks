import copy
import enum
import random
import unittest.mock
from typing import List, Optional

from faker import Faker

from utils import IOUtils


class Session:
    current_time: int  # current time in months
    users: List["User"]
    faker: Faker
    initial_money_in_bank: float

    def __init__(self):
        self.users = []
        self.current_time = 0
        self.faker = Faker()
        self.initial_money_in_bank = 100_000  # 100 thousand euros

    def populate_db(self):
        with unittest.mock.patch(print.__module__ + ".print"):
            for _ in range(10):
                user = User.generate_random_user(self)
                self.users.append(user)

    @property
    def money_in_bank(self):
        money_in_bank = IOUtils.round_float_to_2_decimal_places(
            self.initial_money_in_bank + self.total_user_savings - self.total_user_loans
        )

        if money_in_bank < 0:
            IOUtils.print_header(
                f"\nCRITICAL: Amount in the bank is {money_in_bank}. Money in the bank cannot be negative. "
                f"You broke the bank!\n")
        return money_in_bank

    @property
    def total_user_savings(self):
        return IOUtils.round_float_to_2_decimal_places(
            sum([user.savings_account.savings_amount for user in self.users]))

    @property
    def total_user_loans(self):
        return IOUtils.round_float_to_2_decimal_places(
            sum([sum([loan.sum for loan in user.loans]) for user in self.users]))

    @property
    def total_user_personal_savings(self):
        return IOUtils.round_float_to_2_decimal_places(self.total_user_savings - self.total_user_loans)


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
        amount = float(amount)  # ensure that amount is float
        if amount <= 0:
            raise ValueError("Loan amount can not be negative or zero")
        if amount > 10_000:
            raise ValueError("Bank do not give loans more than €10000")

        self.sum = IOUtils.round_float_to_2_decimal_places(amount)
        self.initiated_at = initiated_at
        # Set fixed loan rate
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

    def apply_interest_rate(self):
        """Applies interest rate to the loan sum"""
        monthly_interest_rate = self.interest_rate / 12
        self.sum = IOUtils.round_float_to_2_decimal_places(self.sum * (1 + monthly_interest_rate))

    def pay(self, amount: float, prefix: str = '') -> LoanStatusEnum:
        """Allow user to pay for a loan and returns the loan status"""
        if not amount > 0:
            raise ValueError("Payment amount can not be negative or zero")
        self.sum -= amount

        if self.sum <= 0:
            self.sum = 0
            self.status = LoanStatusEnum.PAID
            print(prefix + "Loan is paid in full and is closed. Thank you!")
        else:
            print(prefix + f"Loan is partially paid. Thanks! You still owe €{self.sum:.2f} for this loan")
        return self.status

    def pretty_print_loan(self, session: Session, prefix: str = ""):
        loan_print = prefix + f"Loan: €{self.sum:.2f}, initiated at: {self.initiated_at}, " \
                              f"interest rate: {self.interest_rate * 100}%, expired: {self.is_expired(session)}"
        # add the expiration date if the loan is not expired
        if not self.is_expired(session):
            if self.expires_in(session) == 1:
                loan_print = loan_print + ", expires NEXT month"
            else:
                loan_print = loan_print + f", expires in: {self.expires_in(session)} months"
        print(loan_print)

    @staticmethod
    def create_loan_object(session: Session, loan_amount: float):
        """Loan factory method"""
        return Loan(loan_amount, session.current_time)

    def __repr__(self):
        return f"Loan(sum={self.sum}, initiated_at={self.initiated_at}, interest_rate={self.interest_rate})"

    def __str__(self):
        return f"Loan: €{self.sum:.2f}, initiated at {self.initiated_at} month(s) at interest rate of {self.interest_rate * 100}%"


class SavingsAccount:
    savings_amount: float
    interest_rate: float

    @staticmethod
    def define_rate_for_amount(amount: float):
        """Function that sets interest rate depending on the amount of savings

        If the amount of savings is more than €10,000, the interest rate is 5.5%;
        If the amount of savings is less than €10,000, the interest rate is 5%.
        """
        if amount >= 10_000:
            return 0.055
        else:
            return 0.05

    def __init__(self, savings_amount: float):
        savings_amount = float(savings_amount)  # ensure that amount is float
        self.savings_amount = savings_amount
        self.interest_rate = self.define_rate_for_amount(savings_amount)

    def add_savings(self, amount: float):
        if amount <= 0:
            raise ValueError("Deposit amount can not be negative or zero")
        if amount > 1_000_000:
            raise ValueError("Deposit amount can not be more than €1 million")
        self.savings_amount += amount
        print(f"Deposited €{amount}. Current savings: €{self.savings_amount}")

    def withdraw_savings(self, amount: float):
        if amount > self.savings_amount:
            raise ValueError("Not enough savings to withdraw")
        self.savings_amount -= amount
        print(f"Withdrawn €{amount} from savings account. Current savings: ${self.savings_amount}")

    def apply_and_adjust_interest_rate(self, session: Session):
        """Function that applies interest rate to the savings amount and adjusts the interest rate after"""
        monthly_interest_rate = self.interest_rate / 12
        monthly_interest = IOUtils.round_float_to_2_decimal_places(self.savings_amount * monthly_interest_rate)
        self.savings_amount = IOUtils.round_float_to_2_decimal_places(self.savings_amount + monthly_interest)
        self.interest_rate = self.define_rate_for_amount(self.savings_amount)

    def __str__(self):
        return f"Savings Account details: savings: €{self.savings_amount:.2f} at interest_rate of {self.interest_rate * 100}%"


class User:
    username: str
    full_name: str
    loans: List[Loan]
    savings_account: SavingsAccount
    status: UserStatusSavingEnum

    def __init__(self, session: Session, loans: Optional[List[Loan]] = None, savings: int = 0):
        self.full_name = session.faker.unique.first_name() + " " + session.faker.unique.last_name()
        self.username = self.full_name.lower().replace(" ", "_")
        self.loans = loans or []
        self.savings_account = SavingsAccount(savings)
        self.status = UserStatusSavingEnum.ACTIVE

    def add_loan(self, session: Session, loan: Loan):
        if self.status == UserStatusSavingEnum.LOCKED:
            raise ValueError("User is locked")
        if self.status == UserStatusSavingEnum.OVERDUE_LOANS:
            raise ValueError("User has unpaid loans")
        if len(self.loans) >= 3:
            raise ValueError("User can not have more than 3 loans concurrently")

        if session.money_in_bank < loan.sum:
            raise ValueError(
                f"Sorry! Bank do not have enough money to issue the loan. You ask for €{loan.sum} but bank has only "
                f"€{session.money_in_bank}. Please try again later.")

        self.loans.append(loan)
        self.savings_account.savings_amount = IOUtils.round_float_to_2_decimal_places(
            self.savings_account.savings_amount + loan.sum
        )
        print(f"Loan added successfully. €{loan.sum} were deposited to your savings account. Thank you!")

    def pay_loan(self, session: Session, loan: Loan, amount: float, prefix: str = ""):
        """Function that allows user to pay for a loan and removes the loan if it is paid in full

        Function will deduct the respective amount from the savings account"""
        if amount > self.savings_account.savings_amount:
            raise ValueError("Not enough savings to pay for the loan")
        status = loan.pay(amount, prefix=prefix)
        self.savings_account.savings_amount = IOUtils.round_float_to_2_decimal_places(
            self.savings_account.savings_amount - amount
        )

        # Remove loan from the user object if it is paid and keep if is not
        if status == LoanStatusEnum.PAID:
            self.loans.remove(loan)

        # Set user status back to active if all overdue loans are paid
        if self.status == UserStatusSavingEnum.OVERDUE_LOANS and self.has_no_overdue_loans(session):
            print("You have paid out all overdue loans. Your account is set back to ACTIVE. Congratulations!")
            self.status = UserStatusSavingEnum.ACTIVE

    def at_least_one_user_loan_is_overdue(self, session: Session):
        return any([user_loan.is_expired(session) for user_loan in self.loans])

    def has_no_overdue_loans(self, session: Session):
        """Function to check if user has no expired loans.

        Returns True if all loans that user are not expired or user does not have any loans
        Returns False if user has at least one expired loan
        """
        return all([not user_loan.is_expired(session) for user_loan in self.loans])

    def rate_adjustment_is_needed(self) -> bool:
        return self.savings_account.interest_rate != \
            SavingsAccount.define_rate_for_amount(self.savings_account.savings_amount)

    def withdraw_savings(self, session: Session, amount: float):
        if self.status == UserStatusSavingEnum.LOCKED:
            raise ValueError("User is locked")
        if self.status == UserStatusSavingEnum.OVERDUE_LOANS:
            raise ValueError("User has unpaid loans")
        if amount > self.savings_account.savings_amount:
            raise ValueError("Not enough savings to withdraw")
        if session.money_in_bank < amount:
            raise ValueError(
                f"Excuse us! You ask us for €{amount} but there are only €{session.money_in_bank} in the bank left. "
                "Please try again later, deposits money to the bank.")
        self.savings_account.withdraw_savings(amount)

    def deposit_savings(self, deposit_amount: float):
        if self.status == UserStatusSavingEnum.LOCKED:
            raise ValueError("User is locked")
        self.savings_account.add_savings(deposit_amount)

    @property
    def personal_savings_amount(self):
        return self.savings_account.savings_amount - self.total_loans

    @property
    def total_loans(self):
        return IOUtils.round_float_to_2_decimal_places(sum([loan.sum for loan in self.loans]))

    @staticmethod
    def generate_random_user(session: Session):
        """Function that generates a random user with random loans and savings amount"""
        loans = [Loan.create_loan_object(session, random.randint(0, 10_000)) for _ in
                 range(random.randint(0, 3))]
        user = User(session=session, loans=loans, savings=random.randint(0, 30_000))
        fake_session = copy.deepcopy(session)
        fake_session.users.append(user)
        if fake_session.money_in_bank < 0:
            raise ValueError("Random user can not be generated, otherwise bank will not have money left.")

        return user

    def __repr__(self):
        return f"User(username={self.username}, full_name={self.full_name}, loans={self.loans}, " \
               f"{self.savings_account}, status={self.status})"
