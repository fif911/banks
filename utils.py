from typing import Optional, List


class IOUtils:
    @staticmethod
    def input_int(message, lower_bound=None, upper_bound=None):
        while True:
            try:
                value = int(input(message))
                if lower_bound is not None and value < lower_bound:
                    raise ValueError(f"Value must be at least {lower_bound}")
                if upper_bound is not None and value > upper_bound:
                    raise ValueError(f"Value must be at most {upper_bound}")
                return value
            except ValueError as e:
                print("Incorrect value! Try again. Details: " + str(e))

    @staticmethod
    def input_str(message, expected_values: Optional[List[str]] = None):
        while True:
            value = input(message)
            if expected_values is not None and value not in expected_values:
                print(f"Value must be one of {expected_values}")
                continue
            return value

    @staticmethod
    def print_menu_and_return_choice(menu: List[str], intro_message="Select an action:", ) -> int:
        print(intro_message)
        for i, item in enumerate(menu):
            print(f"{i + 1}. {item}")
        menu_option = IOUtils.input_int("Enter the number of the action: ", upper_bound=len(menu), lower_bound=1)
        return menu_option
