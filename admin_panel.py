from entities import Session
from utils import IOUtils


def handle_administration_mode(session: Session):
    print("Welcome to the administrator mode! \n"
          "You can view all the users and their details and run simulations.")
    while True:
        action = IOUtils.print_menu_and_return_choice(
            ["View all users", "Run simulation", "Go one month ahead", "Log out"])
        if action == 1:
            for i, user in enumerate(session.users):
                print(f"{i + 1} - {user.full_name}, Savings: €{user.saving}, status: {user.status}")
                for loan in user.loans:
                    print(" " * 10
                          + f"Loan: €{loan.sum}, initiated at: {loan.initiated_at}, "
                            f"interest_rate {loan.interest_rate}, expired: {loan.is_expired(session)}")
                if not user.loans:
                    print(" " * 10 + "No loans")
        if action == 2:
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
        if action == 3:
            print("Going one month ahead...")
            session.current_time += 1
            # TODO: Go though all users and increase their loans and savings by interest rate
            # check if user has expired loans
            # set status if user has expired loans
            # check the savings and adjust interest rate if needed
            #   serve the loans if possible from savings
            # print the change logs
            session.current_time += 1

            print("Succeeded. Current time is " + str(session.current_time))
        if action == 4:
            print("Logging out...")
            return
