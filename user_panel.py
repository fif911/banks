import enum

from entities import Session, UserStatusSavingEnum, LoanStatusEnum, User, Loan
from utils import IOUtils


def handle_user_deposit_money_action(user):
    deposit_amount = IOUtils.input_float("Enter the amount you want to deposit: ", lower_bound=1, upper_bound=1_000_000)
    user.deposit_savings(deposit_amount)


def handle_user_withdraw_money_action(user):
    withdraw_amount = IOUtils.input_float("Enter the amount you want to withdraw: ", lower_bound=1,
                                          upper_bound=user.saving)
    user.withdraw_savings(withdraw_amount)


def handle_user_take_a_loan_action(session: Session, user: User):
    loan_amount = IOUtils.input_float("Enter the amount of the loan: ", lower_bound=1, upper_bound=10_000)
    new_loan = Loan.issue_loan(session, loan_amount)
    user.add_loan(new_loan)


def handle_user_pay_a_loan_action(user):
    if len(user.loans) == 0:
        print("You have no loans")
        return
    loan_index = IOUtils.print_menu_and_return_choice(user.loans, "Choose the loan you want to pay: ")
    loan = user.loans[loan_index - 1]
    pay_amount = IOUtils.input_float("Enter the amount you want to pay: ", lower_bound=0.01, upper_bound=loan.sum)
    status = loan.pay(pay_amount)

    # remove loan from the user object if it is paid and keep if is not
    if status == LoanStatusEnum.PAID:
        user.loans.remove(loan)


class UserActionEnum(enum.Enum):
    DEPOSIT = 1
    WITHDRAW = 2
    TAKE_A_LOAN = 3
    PAY_A_LOAN = 4
    LOGOUT = 5


def handle_user_mode(session: Session):
    print("Welcome to the user mode!")
    print("Log in as a user:")
    for i, user in enumerate(session.users):
        print(f"{i + 1} - {user.full_name}")
    user_index = IOUtils.input_int("Enter the number of the user: ", upper_bound=len(session.users), lower_bound=1)
    user = session.users[user_index - 1]
    while True:
        print(f"Hello, {user.full_name}!")

        print(f"Your savings account balance is €{user.saving} with interest rate of 0.1%")
        print(f"You have {len(user.loans)} loans. They are:")
        for loan in user.loans:
            loan.pretty_print_loan(session, prefix=" " * 10)
        print(f"Your status is {user.status}")

        user_chosen_action = None  # action that is cho
        if user.status == UserStatusSavingEnum.LOCKED:
            print("This account is locked. You can not do anything. The user was automatically logged out.")
            break
        elif user.status == UserStatusSavingEnum.OVERDUE_LOANS:
            print("You have unpaid loans for more than 12 months. "
                  "You cannot withdraw from savings account or take new loans.")
            action = IOUtils.print_menu_and_return_choice(
                ["Deposit to savings account", "Pay a loan", "Log out"])
            if action == 1:
                user_chosen_action = UserActionEnum.DEPOSIT
            if action == 2:
                user_chosen_action = UserActionEnum.WITHDRAW
            if action == 3:
                user_chosen_action = UserActionEnum.LOGOUT
        else:
            action = IOUtils.print_menu_and_return_choice(
                ["Withdraw from savings account", "Deposit to savings account", "Take a loan", "Pay a loan", "Log out"])
            if action == 1:
                user_chosen_action = UserActionEnum.WITHDRAW
            if action == 2:
                user_chosen_action = UserActionEnum.DEPOSIT
            if action == 3:
                user_chosen_action = UserActionEnum.TAKE_A_LOAN
            if action == 4:
                user_chosen_action = UserActionEnum.PAY_A_LOAN
            if action == 5:
                user_chosen_action = UserActionEnum.LOGOUT

        if user_chosen_action == UserActionEnum.DEPOSIT:
            handle_user_deposit_money_action(user)
        elif user_chosen_action == UserActionEnum.WITHDRAW:
            handle_user_withdraw_money_action(user)
        elif user_chosen_action == UserActionEnum.TAKE_A_LOAN:
            handle_user_take_a_loan_action(session, user)
        elif user_chosen_action == UserActionEnum.PAY_A_LOAN:
            handle_user_pay_a_loan_action(user)

        elif user_chosen_action == UserActionEnum.LOGOUT:
            print("Logging out...")
            return
