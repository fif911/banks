import enum
import uuid
from typing import List, Optional


class UserStatusSavingEnum(enum.Enum, str):
    LOCKED = "LOCKED"
    ACTIVE = "ACTIVE"


class Loan:
    sum: int
    initiated_at: int

    def __init__(self, sum: int, initiated_at: int):
        if sum > 10_000:
            raise ValueError("Bank do not give loans more than $10000")
        self.sum = sum
        self.initiated_at = initiated_at


class User:
    id: uuid.UUID
    loans: List[Loan]
    saving: int
    status: UserStatusSavingEnum

    def __init__(self, loans: Optional[Loan] = None, saving: int = 0):
        self.id = uuid.UUID()
        self.loans = loans or []
        self.saving = saving
        self.status = UserStatusSavingEnum.ACTIVE

    def add_loan(self, loan: Loan):
        if len(self.loans) > 3:
            raise ValueError("User can not have more than 3 loans concurrently")
        self.loans.append(loan)
