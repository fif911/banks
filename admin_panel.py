import copy

from entities import Session, UserStatusSavingEnum, LoanStatusEnum
from utils import IOUtils


def _at_least_one_user_loan_is_overdue(user, session: Session):
    return any([user_loan.is_expired(session) for user_loan in user.loans])


def _user_has_no_expired_loans(user, session: Session):
    """Function to check if user has no expired loans.

    Returns True if all loans that user are not expired or user does not have any loans
    Returns False if user has at least one expired loan
    """
    return all([not user_loan.is_expired(session) for user_loan in user.loans])


def handle_user_list_action(session: Session):
    for i, user in enumerate(session.users):
        print(
            f"{i + 1} - {user.full_name}, Savings: €{user.savings_account.savings_amount:.2f} (at {user.savings_account.interest_rate * 100}%), status: {user.status}")
        for loan in user.loans:
            loan.pretty_print_loan(session, prefix=" " * 10)

        if not user.loans:
            print(" " * 10 + "No loans")


def handle_simulate_action(session: Session):
    IOUtils.print_section("Simulation")
    simulated_time = 0
    while True:
        enter_or_exit = IOUtils.input_str(
            "Click enter to run simulation for 1 month ahead. Type 'exit' to exit. ",
            expected_values=["", "exit"])
        if enter_or_exit == "exit":
            print("Exiting simulation...")
            break
        simulated_time += 1
        print(
            f"Current real time is {session.current_time}. "
            f"Simulation results for {simulated_time} month(s) ahead:")
        print("Done.")


def handle_month_forward_action(session: Session):
    print("Going one month ahead...")
    session.current_time += 1

    for user in session.users:
        print(" " * 10 + f" ---------------- User {user.full_name} (status: {user.status})")
        if user.status == UserStatusSavingEnum.OVERDUE_LOANS:
            if _at_least_one_user_loan_is_overdue(user, session):
                # Lock user if one has overdue status for 1 month and failed to pay all overdue loans on their
                # own during the grace period
                user.status = UserStatusSavingEnum.LOCKED
                print(
                    " " * 20 + "User had overdue loans and failed to pay on their own during the grace period.")
            else:
                # If user has overdue status but has paid the loans on their own during the grace period,
                # their status is set to active
                user.status = UserStatusSavingEnum.ACTIVE
                print(" " * 20 + "User had overdue loans but paid on their own during the grace period "
                                 "==> User was reactivated.")
        if user.status == UserStatusSavingEnum.LOCKED:
            print(" " * 20 + "User is locked. Reason: Overdue unpaid loans.")
            continue

        # Increase loans and savings by interest rate
        for user_loan in user.loans:
            user_loan.apply_interest_rate()
        # Adjust interest rate if needed
        user.savings_account.apply_and_adjust_interest_rate()

        print(" " * 20 + "Interest rate for loans and savings applied.")

        if user.status == UserStatusSavingEnum.ACTIVE:
            if _at_least_one_user_loan_is_overdue(user, session):
                # If user has overdue loans, set their status to overdue
                user.status = UserStatusSavingEnum.OVERDUE_LOANS
                print(" " * 20 + "User has overdue loans. Setting status to overdue.")

        if user.status == UserStatusSavingEnum.OVERDUE_LOANS:
            # If user has overdue loans, try to deduct from savings to cover the loans
            for user_loan in user.loans:
                if user_loan.is_expired(session):
                    # Try to deduct from savings to cover the loans
                    if user.savings_account.savings_amount >= user_loan.sum:
                        # Deduct from payment amount from savings and round to 2 decimal places
                        user.savings_account.savings_amount = IOUtils.round_float_to_2_decimal_places(
                            user.savings_account.savings_amount - user_loan.sum
                        )

                        user_loan.pay(user_loan.sum, prefix=' ' * 20)
                    else:
                        print(
                            " " * 20 + (
                                f"Not enough savings to cover the loan. User status is set to "
                                f"{UserStatusSavingEnum.OVERDUE_LOANS}. "
                                "Next month will be the grace period. User will be locked if they fail "
                                "to pay the loans on their own."))
                        break

            # Remove paid loans
            user.loans = [user_loan for user_loan in user.loans if not user_loan.status == LoanStatusEnum.PAID]

            # If all expired loans were successfully paid, set status back to active
            if _user_has_no_expired_loans(user, session):
                user.status = UserStatusSavingEnum.ACTIVE
                print(" " * 20 + "All loans are paid. Setting status back to active.")

    print("Succeeded. Current time is " + str(session.current_time) + " month(s).\n")


def handle_administration_mode(session: Session):
    IOUtils.print_header("Welcome to the administrator mode!")
    print("You can view all the users and their details and run simulations.")
    while True:
        action = IOUtils.print_menu_and_return_choice(
            ["View all users", "Run simulation", "Go one month ahead", "Log out"])
        if action == 1:
            handle_user_list_action(session)
        if action == 2:
            handle_simulate_action(copy.deepcopy(session))
        if action == 3:
            handle_month_forward_action(session)
        if action == 4:
            print("Logging out...")
            return
