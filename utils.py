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
