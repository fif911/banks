import copy
import unittest.mock
from functools import reduce

from entities import Session, UserStatusSavingEnum, LoanStatusEnum, User
from utils import IOUtils


def _user_in_one_month(user, session: Session) -> User:
    """Function calculates the user status in one month.

    Function will mutate the user object and also return it.
    Thus, if one wants just to calculate the user object - one should deepcopy copied before calling the function.

    Usage example:
    >>> _user_in_one_month(user, session) # will mutate the user object

    If one wants just to perform the calculation but not mutate the user object, one should deepcopy it before calling
    the function:
    >>> user_in_one_month = _user_in_one_month(copy.deepcopy(user), session)
    """
    print(" " * 10 + f" * User {user.full_name} (status: {user.status})")
    if user.status == UserStatusSavingEnum.OVERDUE_LOANS:
        if user.at_least_one_user_loan_is_overdue(session):
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
        print(" " * 20 + "User is LOCKED. Reason: Overdue unpaid loans.")
        return user

    # Increase loans and savings by interest rate that was set at the beginning of the previous month
    for user_loan in user.loans:
        user_loan.apply_interest_rate()

    # Adjust interest rate if needed, s.t. in the next month a new interest rate will be applied
    user.savings_account.apply_and_adjust_interest_rate(session)
    print(" " * 20 + "Interest rate for loans and savings applied.")

    if user.status == UserStatusSavingEnum.ACTIVE:
        # If user has overdue loans, set their status to overdue
        if user.at_least_one_user_loan_is_overdue(session):
            user.status = UserStatusSavingEnum.OVERDUE_LOANS
            print(" " * 20 + "User has overdue loans. Setting status to OVERDUE_LOANS.")

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

        # If all overdue loans were successfully paid, set status back to active
        if user.has_no_overdue_loans(session):
            user.status = UserStatusSavingEnum.ACTIVE
            print(" " * 20 + "All loans are paid. Setting status back to ACTIVE.")
    return user


def handle_user_list_action(session: Session):
    for i, user in enumerate(session.users):
        print(
            f"{i + 1} - {user.full_name}, Savings: €{user.savings_account.savings_amount:.2f} (at {user.savings_account.interest_rate * 100}%), status: {user.status}")
        if user.loans:
            print(" " * 10 + f"User owes to the bank in total €{user.total_loans}. "
                             f"(Note that this amount is added to user's savings account)")
            for loan in user.loans:
                loan.pretty_print_loan(session, prefix=" " * 10)
        else:
            print(" " * 10 + "No loans")


def handle_simulate_action(session: Session):
    """Function that performs simulation

    Function performs a deepcopy of the current session to avoid mutating the original session, performs the simulation
    and prints the results.
    """
    current_real_time = session.current_time
    simulated_session = copy.deepcopy(session)
    del session
    IOUtils.print_section("Simulation")

    i = 0
    while True:
        enter_or_exit = IOUtils.input_str(
            f"Click enter to run simulation for {i + 1} month ahead. Type 'exit' to exit. ",
            expected_values=["", "exit"])
        if enter_or_exit == "exit":
            print("Exiting simulation...")
            break

        simulated_session.current_time += 1
        i += 1
        if i > 30:
            print("Simulation is limited to 30 months ahead. Exiting simulation...\n")
            break
        print(f"Note: Current real time is {current_real_time}.")
        IOUtils.print_section(
            f"Simulation results for {i} month(s) ahead:")

        # Perform one month forward action with suppressed prints for simulated session
        users_in_one_month = []
        for user in simulated_session.users:
            with unittest.mock.patch(print.__module__ + ".print"):
                user_in_one_month = _user_in_one_month(copy.deepcopy(user), simulated_session)
            print(" " * 10 + f" * User {user_in_one_month.full_name} "
                             f"will have status: {user_in_one_month.status}")
            print(" " * 20 + f"User will have savings: €{user_in_one_month.savings_account.savings_amount:.2f} "
                             f"at interest rate {user_in_one_month.savings_account.interest_rate * 100}%")
            if len(user_in_one_month.loans):
                user_total_in_loans = IOUtils.round_float_to_2_decimal_places(
                    reduce(lambda a, b: a + b, [loan.sum for loan in user_in_one_month.loans])
                )
                print(
                    " " * 20 + f"User will have total loans {user_total_in_loans}€ "
                               f"(applied corresponding interest rate)")
            else:
                print(" " * 20 + "User user will have €0 in loans.")
            users_in_one_month.append(user_in_one_month)

        simulated_session.users = users_in_one_month  # save calculated users to the session

        # Suppress print that may be called in the function not to give out the vulnerability of the system so easily
        with unittest.mock.patch(print.__module__ + ".print"):
            money_in_bank = simulated_session.money_in_bank
        print(" " * 5 + f" * Total amount of money in the bank will be €{money_in_bank:.2f}")
        print("Done.")


def handle_month_forward_action(session: Session):
    print("Going one month ahead...")
    session.current_time += 1

    for user in session.users:
        _user_in_one_month(user, session)

    print("Succeeded. Current time is " + str(session.current_time) + " month(s).\n")


def handle_administration_mode(session: Session):
    IOUtils.print_header("Welcome to the administrator mode!")
    print("You can view all the users and their details, run simulations and go one month ahead.")

    while True:
        print("\n" + "-" * 10 + " Administrator dashboard " + "-" * 10)
        print(f" * The initial amount of the money the bank had €{session.initial_money_in_bank}.")
        print(f" * The current amount money in the bank is €{session.money_in_bank:.2f}")
        print(f" * Total amount of user savings in the bank is €{session.total_user_savings:.2f} "
              f"(including amount they obtained by taking loans).")
        print(f" * Total amount of user personal savings €{session.total_user_personal_savings:.2f} "
              f"(excluding amount they obtained by taking loans).")
        print(f" * Total amount of user loans is €{session.total_user_loans:.2f}.")
        print(" * The current time is " + str(session.current_time) + " month(s).")
        print("-" * 10 + " End of your dashboard " + "-" * 10)

        action = IOUtils.print_menu_and_return_choice(
            ["View all users", "Run simulation", "Go one month ahead", "Add random customer", "Log out"])
        if action == 1:
            handle_user_list_action(session)
        if action == 2:
            handle_simulate_action(session)
        if action == 3:
            handle_month_forward_action(session)
        if action == 4:
            print("Adding a random customer...")
            try:
                session.users.append(User.generate_random_user(session))
            except ValueError as e:
                print("Failed to add a random user. Error: " + str(e) + "\n")
                continue
            print("Done.")
        if action == 5:
            print("Logging out...")
            return
