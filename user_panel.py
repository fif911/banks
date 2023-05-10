import enum

from entities import Session, UserStatusSavingEnum, LoanStatusEnum, User, Loan
from utils import IOUtils

USER_MENU_PROMPT_MESSAGE = "Choose the action from the Main User Menu: "


def print_user_dashboard(user: User, session: Session):
    print("-" * 10 + " Your dashboard " + "-" * 10)
    print(
        f"Your savings account has €{user.savings_account.savings_amount} at interest rate of {user.savings_account.interest_rate * 100}% (Note: Saving Account includes amount of money added with loans that you have taken)")
    print(f"Your total €{user.personal_savings_amount:.2f} in Personal Savings.")
    if user.personal_savings_amount < 0:
        print(" " * 10 + " * (Negative Personal Savings shows how much you have to deposit to cover all your loans)")
    print()
    if user.loans:
        print(f"You have {len(user.loans)} loans. They are:")
        for loan in user.loans:
            loan.pretty_print_loan(session, prefix=" " * 10)
    if not user.loans:
        print("You have no loans.")
    print(f"Your status is {user.status}")

    print("\nNotification center:")
    notifications = []
    if user.status == UserStatusSavingEnum.OVERDUE_LOANS:
        notifications.append(
            " * You have overdue loans for more than 12 months. "
            "You cannot withdraw from savings account or take new loans.", )
        notifications.append(
            " * You have overdue loans. Please pay them during this month otherwise the account will be locked.")
    if user.rate_adjustment_is_needed():
        notifications.append(" * Due to your (or automatic) recent actions your savings interest rate will be "
                             "adjusted at the begging of the next month.")
    if user.personal_savings_amount < 0:
        notifications.append(" * Your personal savings account has negative balance. "
                             "Consider depositing money to pay off your loans.")
    if not notifications:
        print(" * You have no notifications.")
    else:
        print("\n".join(notifications))

    print("-" * 10 + " End of your dashboard " + "-" * 10)


def handle_user_deposit_money_action(user):
    deposit_amount = IOUtils.input_float("Enter the amount you want to deposit (at least €1 and at most €1 million): ",
                                         lower_bound=1, upper_bound=1_000_000)
    try:
        user.deposit_savings(deposit_amount)
    except ValueError as e:
        print("Error: ", e)


def handle_user_withdraw_money_action(session, user: User):
    if user.savings_account.savings_amount <= 0:
        print("You have no money in your savings account. Thus it is not possible to withdraw money.")
        return
    withdraw_amount = IOUtils.input_float("Enter the amount you want to withdraw: ", lower_bound=1,
                                          upper_bound=user.savings_account.savings_amount)
    try:
        user.withdraw_savings(session, withdraw_amount)
    except ValueError as e:
        print("Error: ", e)


def handle_user_take_a_loan_action(session: Session, user: User):
    if len(user.loans) >= 3:
        print("User can not have more than 3 loans concurrently")
        return
    loan_amount = IOUtils.input_float("Enter the amount of the loan (at least €1 and at most €10000): ", lower_bound=1,
                                      upper_bound=10_000)
    new_loan = Loan.create_loan_object(session, loan_amount)
    try:
        user.add_loan(session, new_loan)
    except ValueError as e:
        print("Error: ", e)


def handle_user_pay_a_loan_action(session: Session, user: User):
    if len(user.loans) == 0:
        print("You have no loans")
        return
    if user.savings_account.savings_amount <= 0:
        print("You have no money in your savings account. Thus it is not possible to pay a loan. Deposit money first.")
        return
    loan_index = IOUtils.print_menu_and_return_choice(user.loans, "Choose the loan you want to pay: ",
                                                      "Enter the ID of the loan you want to pay for: ")
    loan = user.loans[loan_index - 1]

    sum_to_pay_at_most = min(user.savings_account.savings_amount, loan.sum)
    if loan.sum > sum_to_pay_at_most:
        print(
            "Note that you cannot fully cover this loan due to insufficient funds in your savings account."
            "Deposit additional money after to fully cover the loan.")

    pay_amount = IOUtils.input_float(
        f"Enter the amount you want to pay (at least €0.01 and at most €{sum_to_pay_at_most}): ",
        lower_bound=0.01, upper_bound=loan.sum)

    try:
        user.pay_loan(session, loan, pay_amount)
    except ValueError as e:
        print("Error: ", e)


class UserActionEnum(enum.Enum):
    DEPOSIT = 1
    WITHDRAW = 2
    TAKE_A_LOAN = 3
    PAY_A_LOAN = 4
    LOGOUT = 5


def handle_user_mode(session: Session):
    IOUtils.print_header("Welcome to the user mode!")
    print("Log in as a user:")
    for i, user in enumerate(session.users):
        print(f"{i + 1} - {user.full_name}")
    user_index = IOUtils.input_int("Enter the number of the user: ", upper_bound=len(session.users), lower_bound=1)
    user = session.users[user_index - 1]

    IOUtils.print_section(f"Hello, {user.full_name}!")
    while True:
        print_user_dashboard(user, session)

        user_chosen_action = None  # action that is cho
        if user.status == UserStatusSavingEnum.LOCKED:
            print("This account is locked. You can not do anything. The user was automatically logged out.")
            break
        elif user.status == UserStatusSavingEnum.OVERDUE_LOANS:
            action = IOUtils.print_menu_and_return_choice(
                ["Deposit to savings account", "Pay a loan", "Log out"],
                USER_MENU_PROMPT_MESSAGE)
            if action == 1:
                user_chosen_action = UserActionEnum.DEPOSIT
            if action == 2:
                user_chosen_action = UserActionEnum.PAY_A_LOAN
            if action == 3:
                user_chosen_action = UserActionEnum.LOGOUT
        else:
            action = IOUtils.print_menu_and_return_choice(
                ["Withdraw from savings account", "Deposit to savings account", "Take a loan", "Pay a loan", "Log out"],
                USER_MENU_PROMPT_MESSAGE)
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
            handle_user_withdraw_money_action(session, user)
        elif user_chosen_action == UserActionEnum.TAKE_A_LOAN:
            handle_user_take_a_loan_action(session, user)
        elif user_chosen_action == UserActionEnum.PAY_A_LOAN:
            handle_user_pay_a_loan_action(session, user)

        elif user_chosen_action == UserActionEnum.LOGOUT:
            print("Logging out...")
            return
