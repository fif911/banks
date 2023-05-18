from entities import Session, Loan, LoanStatusEnum, SavingsAccount, User, UserStatusSavingEnum
import unittest
import admin_panel as admin
from mutpy import commandline    


class LoanTest(unittest.TestCase):
    def test_mt_5(self):
        session = Session()  # instantiate the session
        loan = Loan(100, 0)
        self.assertEqual(loan.expires_in(session), 12)

    def test_mt_6(self):
        session = Session()  # instantiate the session
        session.current_time = 5
        loan = Loan(100, 0)
        self.assertEqual(loan.expires_in(session), 7)

    def test_mt_7(self):
        session = Session()  # instantiate the session
        session.current_time = 12
        loan = Loan(100, 0)
        self.assertEqual(loan.expires_in(session), 0)

    def test_mt_8(self):
        session = Session()  # instantiate the session
        session.current_time = 14
        loan = Loan(100, 0)
        self.assertEqual(loan.expires_in(session), 0)

    def test_test_15a(self):
        loan = Loan(2000, 0)
        loan.apply_interest_rate()
        self.assertEqual(loan.sum, 2017.5)

    def test_test_15b(self):
        loan = Loan(1000, 0)
        loan.apply_interest_rate()
        self.assertEqual(loan.sum, 1008.33)

    def test_test_4a(self):
        loan = Loan(100, 0)
        loan.pay(0.01)
        self.assertEqual(loan.sum, 99.99)

    def test_test_5a(self):
        loan = Loan(150, 0)
        loan.pay(150)
        self.assertEqual(loan.sum, 0)
        self.assertEqual(loan.status, LoanStatusEnum.PAID)

    def test_mt_9(self):
        loan = Loan(150, 0)
        with self.assertRaises(ValueError):
            loan.pay(0)

    def test_mt_10(self):
        loan = Loan(150, 0)
        with self.assertRaises(ValueError):
            loan.pay(-100)

    def test_test_10a(self):
        session = Session()
        loan = Loan.create_loan_object(session, 1000)
        self.assertEqual(loan.sum, 1000)
        self.assertEqual(loan.interest_rate, 0.10)
    
    def test_mt_11(self):
        session = Session()
        loan = Loan.create_loan_object(session, 10000)
        self.assertEqual(loan.sum, 10000)
        self.assertEqual(loan.interest_rate, 0.105)
    
    def test_mt_12(self):
        session = Session()
        with self.assertRaises(ValueError):
            Loan.create_loan_object(session, 0)

    def test_mt_13(self):
        session = Session()
        with self.assertRaises(ValueError):
            Loan.create_loan_object(session, 10000.1)
    
class SavingsTest(unittest.TestCase):
    def test_test_15i(self):
        acc = SavingsAccount(5000)
        self.assertEqual(acc.interest_rate, 0.05)

    def test_test_15j(self):
        acc = SavingsAccount(10000)
        self.assertEqual(acc.interest_rate, 0.055)

    def test_test_2a(self):
        acc = SavingsAccount(5000)
        acc.add_savings(2000)
        self.assertEqual(acc.savings_amount, 7000)

    def test_mt_14(self):
        acc = SavingsAccount(5000)
        with self.assertRaises(ValueError):
            acc.add_savings(0)

    def test_mt_15(self):
        acc = SavingsAccount(5000)
        with self.assertRaises(ValueError):
            acc.add_savings(2000000)

    def test_test_7a(self):
        acc = SavingsAccount(5000)
        acc.withdraw_savings(1)
        self.assertEqual(acc.savings_amount, 4999)

    def test_mt_16(self):
        acc = SavingsAccount(100)
        with self.assertRaises(ValueError):
            acc.withdraw_savings(200)

    def test_test_15k(self):
        session = Session()
        acc = SavingsAccount(5000)
        acc.apply_and_adjust_interest_rate(session)
        self.assertEqual(acc.savings_amount, 5020.83)
        self.assertEqual(acc.interest_rate, 0.05)

    def test_test_15l(self):
        session = Session()
        acc = SavingsAccount(10000)
        acc.interest_rate = 0.05
        acc.apply_and_adjust_interest_rate(session)
        self.assertEqual(acc.savings_amount, 10041.67)
        self.assertEqual(acc.interest_rate, 0.055)


class UserTest(unittest.TestCase):
    def test_test_10b(self):
        session = Session()
        loan = Loan(5000, 0)
        user = User(session, savings = 100)
        user.add_loan(session, loan)
        self.assertEqual(user.savings_account.savings_amount, 5100)
        self.assertEqual(len(user.loans), 1)

    def test_mt_17(self):
        session = Session()
        loan = Loan(2000, 0)
        user = User(session, savings = 100)
        user.status = UserStatusSavingEnum.LOCKED
        with self.assertRaises(ValueError):
            user.add_loan(session, loan)

    def test_mt_18(self):
        session = Session()
        loan = Loan(2000, 0)
        user = User(session, savings = 100)
        user.status = UserStatusSavingEnum.OVERDUE_LOANS
        with self.assertRaises(ValueError):
            user.add_loan(session, loan)

    def test_mt_19(self):
        session = Session()
        loan = Loan(2000, 0)
        user = User(session, loans = [loan, loan, loan] ,savings = 100)
        with self.assertRaises(ValueError):
            user.add_loan(session, loan)

    def test_mt_20(self):
        session = Session()
        session.initial_money_in_bank = 100 #no users in the session so the only money available is from the initial amount
        loan = Loan(2000, 0)
        user = User(session, savings = 100)
        with self.assertRaises(ValueError):
            user.add_loan(session, loan)

    def test_mt_23(self):
        session = Session()
        loan = Loan(800, 0)
        user = User(session, [loan], 2000)
        user.pay_loan(session, loan, 500)
        self.assertEqual(user.savings_account.savings_amount, 1500)
        self.assertEqual(loan.sum, 300)

    def test_mt_24(self):
        session = Session()
        session.current_time = 12
        loan = Loan(1000, 0)
        user = User(session, [loan], 2000)
        user.status = UserStatusSavingEnum.OVERDUE_LOANS
        user.pay_loan(session, loan, 500)
        self.assertEqual(user.savings_account.savings_amount, 1500)
        self.assertEqual(loan.sum, 500)
        self.assertEqual(user.status, UserStatusSavingEnum.OVERDUE_LOANS)

    def test_mt_25(self):
        session = Session()
        session.current_time = 12
        loan = Loan(1000, 0)
        user = User(session, [loan], 2000)
        user.status = UserStatusSavingEnum.OVERDUE_LOANS
        user.pay_loan(session, loan, 1000)
        self.assertEqual(user.savings_account.savings_amount, 1000)
        self.assertEqual(loan.sum, 0)
        self.assertEqual(loan.status, LoanStatusEnum.PAID)
        self.assertEqual(len(user.loans), 0)
        self.assertEqual(user.status, UserStatusSavingEnum.ACTIVE)

    def test_mt_27(self):
        session = Session()
        loan = Loan(1000, 0)
        user = User(session, [loan], 100)
        with self.assertRaises(ValueError):
            user.pay_loan(session, loan, 1000)

    def test_test_15e(self):
        session = Session()
        session.current_time = 12
        loan = Loan(1000, 0)
        user = User(session, [loan], 100)
        self.assertEqual(user.at_least_one_user_loan_is_overdue(session), True)

    def test_test_15f(self):
        session = Session()
        session.current_time = 1
        loan = Loan(1000, 0)
        user = User(session, [loan], 100)
        self.assertEqual(user.at_least_one_user_loan_is_overdue(session), False)

    def test_test_15g(self):
        session = Session()
        session.current_time = 1
        loan = Loan(1000, 0)
        user = User(session, [loan], 100)
        self.assertEqual(user.has_no_overdue_loans(session), True)

    def test_test_15h(self):
        session = Session()
        session.current_time = 12
        loan = Loan(1000, 0)
        user = User(session, [loan], 100)
        self.assertEqual(user.has_no_overdue_loans(session), False)

    def test_mt_28(self):
        session = Session()
        user = User(session, savings=10000)
        user.savings_account.interest_rate = 0.05
        self.assertEqual(user.rate_adjustment_is_needed(), True)

    def test_mt_29(self):
        session = Session()
        user = User(session, savings=10000)
        user.savings_account.interest_rate = 0.055
        self.assertEqual(user.rate_adjustment_is_needed(), False)

    def test_test_7b(self):
        session = Session()
        user = User(session, savings=5000)
        user.withdraw_savings(session, 1)
        self.assertEqual(user.savings_account.savings_amount, 4999)

    def test_mt_30(self):
        session = Session()
        user = User(session, savings=100)
        with self.assertRaises(ValueError):
            user.withdraw_savings(session, 300)

    def test_mt_31(self):
        session = Session()
        user = User(session, savings=1000)
        user.status = UserStatusSavingEnum.OVERDUE_LOANS
        with self.assertRaises(ValueError):
            user.withdraw_savings(session, 300)

    def test_mt_32(self):
        session = Session()
        user = User(session, savings=1000)
        user.status = UserStatusSavingEnum.LOCKED
        with self.assertRaises(ValueError):
            user.withdraw_savings(session, 300)

    def test_mt_33(self):
        session = Session()
        session.initial_money_in_bank = 500
        user = User(session, savings=1000)
        user.status = UserStatusSavingEnum.LOCKED
        with self.assertRaises(ValueError):
            user.withdraw_savings(session, 1000)

    def test_test_2b(self):
        session = Session()
        user = User(session, savings=5000)
        user.deposit_savings(2000)
        self.assertEqual(user.savings_account.savings_amount, 7000)

    def test_mt_34(self):
        session = Session()
        user = User(session, savings=5000)
        user.status = UserStatusSavingEnum.LOCKED
        with self.assertRaises(ValueError):
            user.deposit_savings(2000)

class AdminTest(unittest.TestCase):
    def test_mt_41(self):
        session = Session()
        user = User(session, savings=15000)
        new_user = admin._user_in_one_month(user, session)
        self.assertEqual(new_user.savings_account.savings_amount, 15068.75)

    def test_mt_42(self):
        session = Session()
        user = User(session, savings=15000)
        user.savings_account.interest_rate = 0.05
        new_user = admin._user_in_one_month(user, session)
        self.assertEqual(new_user.savings_account.savings_amount, 15062.5)
        self.assertEqual(new_user.savings_account.interest_rate, 0.055)

    def test_mt_43(self):
        session = Session()
        user = User(session, savings=1000)
        new_user = admin._user_in_one_month(user, session)
        self.assertEqual(new_user.savings_account.savings_amount, 1004.17)

    def test_mt_44(self):
        session = Session()
        user = User(session, savings=1000)
        user.savings_account.interest_rate = 0.055
        new_user = admin._user_in_one_month(user, session)
        self.assertEqual(new_user.savings_account.savings_amount, 1004.58)
        self.assertEqual(new_user.savings_account.interest_rate, 0.05)

    def test_mt_45(self):
        session = Session()
        loan = Loan(100, 0)
        user = User(session, loans=[loan], savings=1000)
        new_user = admin._user_in_one_month(user, session)
        self.assertEqual(new_user.savings_account.savings_amount, 1004.17)
        self.assertEqual(new_user.loans[0].sum, 100.83)

    def test_mt_46(self):
        session = Session()
        session.current_time = 12
        loan = Loan(100, 0)
        user = User(session, loans=[loan], savings=1000)
        new_user = admin._user_in_one_month(user, session)
        self.assertEqual(new_user.savings_account.savings_amount, 903.34)
        self.assertEqual(len(new_user.loans), 0)
        self.assertEqual(new_user.status, UserStatusSavingEnum.ACTIVE)

    def test_mt_47(self):
        session = Session()
        session.current_time = 13
        user = User(session, savings=1000)
        user.status = UserStatusSavingEnum.OVERDUE_LOANS
        new_user = admin._user_in_one_month(user, session)
        self.assertEqual(new_user.savings_account.savings_amount, 1004.17)
        self.assertEqual(new_user.status, UserStatusSavingEnum.ACTIVE)

    def test_mt_48(self):
        session = Session()
        session.current_time = 12
        loan = Loan(100, 0)
        user = User(session, loans=[loan], savings=1000)
        user.status = UserStatusSavingEnum.OVERDUE_LOANS
        new_user = admin._user_in_one_month(user, session)
        self.assertEqual(new_user.savings_account.savings_amount, 1000)
        self.assertEqual(new_user.status, UserStatusSavingEnum.LOCKED)

    def test_mt_49(self):
        session = Session()
        session.current_time = 12
        loan = Loan(100, 0)
        user = User(session, loans=[loan], savings=0)
        new_user = admin._user_in_one_month(user, session)
        self.assertEqual(new_user.savings_account.savings_amount, 0)
        self.assertEqual(new_user.loans[0].sum, 100.83)
        self.assertEqual(new_user.status, UserStatusSavingEnum.OVERDUE_LOANS)

    def test_mt_50(self):
        session = Session()
        session.current_time = 12
        loan = Loan(100, 0)
        user = User(session, loans=[loan], savings=1000)
        user.status = UserStatusSavingEnum.LOCKED
        new_user = admin._user_in_one_month(user, session)
        self.assertEqual(new_user.savings_account.savings_amount, 1000)
        self.assertEqual(new_user.status, UserStatusSavingEnum.LOCKED)

    def test_mt_51(self):
        session = Session()
        session.current_time = 12
        loan = Loan(100, 0)
        user = User(session, loans=[loan], savings=50)
        new_user = admin._user_in_one_month(user, session)
        self.assertEqual(new_user.savings_account.savings_amount, 50.21)
        self.assertEqual(new_user.loans[0].sum, 100.83)
        self.assertEqual(new_user.status, UserStatusSavingEnum.OVERDUE_LOANS)

if __name__ == '__main__':
    unittest.main()