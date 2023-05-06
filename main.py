from admin_panel import handle_administration_mode
from entities import Session
from user_panel import handle_user_mode
from utils import IOUtils

if __name__ == "__main__":
    session = Session()  # instantiate the session
    session.populate_db()

    while True:
        print("Welcome to the bank!")
        mode = IOUtils.print_menu_and_return_choice(["User mode", "Administrator mode", "Exit the program"],
                                                    "Choose the mode:")
        if mode == 1:
            handle_user_mode(session)
        if mode == 2:
            handle_administration_mode(session)
        if mode == 3:
            print("Exiting the program...")
            break
