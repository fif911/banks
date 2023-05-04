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
        self.admins = []
        self.current_time = 0
        self.faker = Faker()

    def populate_db(self):
        for _ in range(10):
            user = User(self, saving=10_000)
            for _ in range(random.randint(0, 3)):
                user.add_loan(Loan(1000, self.current_time))
            self.users.append(user)


class UserStatusSavingEnum(str, enum.Enum):
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

    def __repr__(self):
        return f"User(username={self.username}, full_name={self.full_name}, loans={self.loans}, saving={self.saving}, status={self.status})"


if __name__ == "__main__":
    print("Welcome to the bank!")
    session = Session()
    session.populate_db()

    print("Choose the mode:"
          "\n1. Im am the user"
          "\n2. I am the administrator")
    mode: int = IOUtils.input_int("Enter the mode (1 or 2): ", upper_bound=2, lower_bound=1)
    if mode == 1:
        print("Welcome to the user mode!")
        print("Log in as a user:")
        for i, user in enumerate(session.users):
            print(f"{i + 1} - {user.full_name}")
        user_index = IOUtils.input_int("Enter the number of the user: ", upper_bound=len(session.users), lower_bound=1)
        user = session.users[user_index - 1]
        print(f"Hello, {user.full_name}!")
    if mode == 2:
        print("Welcome to the administrator mode! \n"
              "You can view all the users and their details and run simulations.")
        print("Select an action:\n"
              "1. View all users\n"
              "2. Run simulation")
        action = IOUtils.input_int("Enter the number of the action: ", upper_bound=2, lower_bound=1)
        if action == 1:
            for i, user in enumerate(session.users):
                print(f"{i + 1} - {user.full_name}, Savings: {user.saving}, status: {user.status}")
                for loan in user.loans:
                    print(
                        " " * 10 + f"Loan: {loan.sum}, initiated at: {loan.initiated_at}, time left: {loan.initiated_at + 12 - session.current_time}")
                if not user.loans:
                    print(" " * 10 + "No loans")
