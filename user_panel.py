from entities import Session, UserStatusSavingEnum
from utils import IOUtils


def handle_user_mode(session: Session):
    print("Welcome to the user mode!")
    print("Log in as a user:")
    for i, user in enumerate(session.users):
        print(f"{i + 1} - {user.full_name}")
    user_index = IOUtils.input_int("Enter the number of the user: ", upper_bound=len(session.users), lower_bound=1)
    user = session.users[user_index - 1]
    while True:
        print(f"Hello, {user.full_name}!")
        if user.status == UserStatusSavingEnum.LOCKED:
            print("This account is locked. You can not do anything.")
            break
        print(f"Your savings account balance is €{user.saving} with interest rate of 0.1%")
        print(f"You have {len(user.loans)} loans. They are:")
        for loan in user.loans:
            print(f"Loan: €{loan.sum}, initiated at: {loan.initiated_at}, "
                  f"interest_rate {loan.interest_rate}, expired: {loan.is_expired(session)}")
        print(f"Your status is {user.status}")
        if user.status == UserStatusSavingEnum.UNPAID_LOANS:
            print("You have unpaid loans for more than 12 months. "
                  "You cannot withdraw from savings account or take new loans.")
            action = IOUtils.print_menu_and_return_choice(
                ["Deposit to savings account", "Pay a loan", "Log out"])
            if action == 3:
                print("Logging out...")
                return
        else:
            action = IOUtils.print_menu_and_return_choice(
                ["Withdraw from savings account", "Deposit to savings account", "Take a loan", "Pay a loan", "Log out"])
            if action == 5:
                print("Logging out...")
                return