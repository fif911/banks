from typing import Optional, List


class IOUtils:
    @staticmethod
    def round_float_to_2_decimal_places(value: float) -> float:
        """Function that rounds the float value to 2 decimal places"""
        return round(value, 2)

    @staticmethod
    def input_int(message, lower_bound=None, upper_bound=None) -> int:
        """Function that asks the user for input of the integer value withing specified range and returns the value"""
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
    def input_float(message, lower_bound=None, upper_bound=None) -> float:
        """Function that asks the user for input of the float value withing specified range and returns the value

        Function rounds the inputted float to 2 decimal places"""
        while True:
            try:
                value = float(input(
                    message + " \nNote: use dot as a decimal separator and the maximum precision is 2 "
                              "(otherwise the value will be rounded to 2 decimal places)"))
                if lower_bound is not None and value < lower_bound:
                    raise ValueError(f"Value must be at least {lower_bound}")
                if upper_bound is not None and value > upper_bound:
                    raise ValueError(f"Value must be at most {upper_bound}")
                return IOUtils.round_float_to_2_decimal_places(value)
            except ValueError as e:
                print("Incorrect value! Try again. Details: " + str(e))

    @staticmethod
    def input_str(message, expected_values: Optional[List[str]] = None) -> str:
        """Function that asks the user for input of the preselected string values and returns the value

        Function repeats until the user enters a valid value"""
        while True:
            value = input(message)
            if expected_values is not None and value not in expected_values:
                print(f"Value must be one of {expected_values}")
                continue
            return value

    @staticmethod
    def print_menu_and_return_choice(menu: List[str], intro_message="Select an action:", ) -> int:
        """Print menu and return the number of the selected action

        Function repeats until the user enters a valid number
        """
        print(intro_message)
        for i, item in enumerate(menu):
            print(f"{i + 1}. {item}")
        menu_option = IOUtils.input_int("Enter the number of the action: ", upper_bound=len(menu), lower_bound=1)
        return menu_option
