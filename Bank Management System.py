import json
import random
from datetime import datetime


# ============================================================
# Custom Exceptions
# ============================================================

class BankError(Exception):
    pass


class InvalidAmountError(BankError):
    pass


class InsufficientFundsError(BankError):
    pass


class AccountNotFoundError(BankError):
    pass


class InvalidPinError(BankError):
    pass


class AccountClosedError(BankError):
    pass


# ============================================================
# Transaction Class
# ============================================================

class Transaction:

    def __init__(
        self,
        transaction_type,
        amount,
        balance_after,
        description=""
    ):
        self.transaction_type = transaction_type
        self.amount = amount
        self.balance_after = balance_after
        self.description = description
        self.timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def __str__(self):
        return (
            f"{self.timestamp} | "
            f"{self.transaction_type:<15} | "
            f"Amount: ${self.amount:.2f} | "
            f"Balance: ${self.balance_after:.2f}"
        )

    def to_dict(self):
        return {
            "transaction_type": self.transaction_type,
            "amount": self.amount,
            "balance_after": self.balance_after,
            "description": self.description,
            "timestamp": self.timestamp
        }


# ============================================================
# BankAccount Class
# ============================================================

class BankAccount:

    def __init__(
        self,
        owner,
        pin,
        balance=0
    ):
        self.account_number = None
        self.owner = owner

        # Encapsulation
        self.__pin = pin
        self.__balance = balance

        self.is_active = True

        self.transactions = []

        if balance > 0:
            self.add_transaction(
                "OPENING",
                balance,
                "Initial balance"
            )

    # --------------------------------------------------------
    # Balance Property
    # --------------------------------------------------------

    @property
    def balance(self):
        return self.__balance

    # --------------------------------------------------------
    # Add Transaction
    # --------------------------------------------------------

    def add_transaction(
        self,
        transaction_type,
        amount,
        description=""
    ):
        transaction = Transaction(
            transaction_type,
            amount,
            self.__balance,
            description
        )

        self.transactions.append(transaction)

    # --------------------------------------------------------
    # Check Account Status
    # --------------------------------------------------------

    def check_active(self):

        if not self.is_active:
            raise AccountClosedError(
                "Account is closed."
            )

    # --------------------------------------------------------
    # Verify PIN
    # --------------------------------------------------------

    def verify_pin(self, pin):

        self.check_active()

        return self.__pin == pin

    # --------------------------------------------------------
    # Change PIN
    # --------------------------------------------------------

    def change_pin(
        self,
        old_pin,
        new_pin
    ):

        self.check_active()

        if self.__pin != old_pin:
            raise InvalidPinError(
                "Incorrect old PIN."
            )

        if (
            not new_pin.isdigit()
            or len(new_pin) != 4
        ):
            raise InvalidPinError(
                "PIN must contain exactly 4 digits."
            )

        self.__pin = new_pin

    # --------------------------------------------------------
    # Deposit
    # --------------------------------------------------------

    def deposit(self, amount):

        self.check_active()

        if amount <= 0:
            raise InvalidAmountError(
                "Amount must be greater than zero."
            )

        self.__balance += amount

        self.add_transaction(
            "DEPOSIT",
            amount,
            "Money deposited"
        )

    # --------------------------------------------------------
    # Withdraw
    # --------------------------------------------------------

    def withdraw(self, amount):

        self.check_active()

        if amount <= 0:
            raise InvalidAmountError(
                "Amount must be greater than zero."
            )

        if amount > self.__balance:
            raise InsufficientFundsError(
                "Insufficient balance."
            )

        self.__balance -= amount

        self.add_transaction(
            "WITHDRAW",
            amount,
            "Money withdrawn"
        )

    # --------------------------------------------------------
    # Transfer
    # --------------------------------------------------------

    def transfer(
        self,
        target_account,
        amount
    ):

        self.check_active()
        target_account.check_active()

        if amount <= 0:
            raise InvalidAmountError(
                "Amount must be greater than zero."
            )

        if amount > self.__balance:
            raise InsufficientFundsError(
                "Insufficient balance."
            )

        self.__balance -= amount
        target_account.__balance += amount

        self.add_transaction(
            "TRANSFER OUT",
            amount,
            f"To {target_account.account_number}"
        )

        target_account.add_transaction(
            "TRANSFER IN",
            amount,
            f"From {self.account_number}"
        )

    # --------------------------------------------------------
    # Close Account
    # --------------------------------------------------------

    def close_account(self):

        self.check_active()

        if self.__balance != 0:
            raise BankError(
                "Balance must be zero before closing."
            )

        self.is_active = False

    # --------------------------------------------------------
    # Transaction History
    # --------------------------------------------------------

    def show_transactions(self):

        if not self.transactions:
            print("No transactions found.")
            return

        print("\n" + "=" * 80)
        print("TRANSACTION HISTORY")
        print("=" * 80)

        for transaction in self.transactions:
            print(transaction)

        print("=" * 80)

    # --------------------------------------------------------
    # Display Account
    # --------------------------------------------------------

    def display(self):

        status = (
            "Active"
            if self.is_active
            else "Closed"
        )

        print("\n" + "-" * 50)
        print(f"Account Number : {self.account_number}")
        print(f"Owner          : {self.owner}")
        print(f"Balance        : ${self.__balance:.2f}")
        print(f"Status         : {status}")
        print("-" * 50)

    # --------------------------------------------------------
    # Convert Account To Dictionary
    # --------------------------------------------------------

    def to_dict(self):

        return {
            "account_number": self.account_number,
            "owner": self.owner,
            "pin": self.__pin,
            "balance": self.__balance,
            "is_active": self.is_active,

            "transactions": [
                {
                    "transaction_type":
                        t.transaction_type,

                    "amount":
                        t.amount,

                    "balance_after":
                        t.balance_after,

                    "description":
                        t.description,

                    "timestamp":
                        t.timestamp
                }

                for t in self.transactions
            ]
        }


# ============================================================
# Bank Class
# ============================================================

class Bank:

    def __init__(self, name):

        self.name = name

        # Dictionary:
        # account_number -> BankAccount
        self.accounts = {}

    # --------------------------------------------------------
    # Generate Account Number
    # --------------------------------------------------------

    def generate_account_number(self):

        while True:

            number = str(
                random.randint(
                    10000000,
                    99999999
                )
            )

            if number not in self.accounts:
                return number

    # --------------------------------------------------------
    # Create Account
    # --------------------------------------------------------

    def create_account(
        self,
        owner,
        pin,
        initial_balance=0
    ):

        account = BankAccount(
            owner,
            pin,
            initial_balance
        )

        account_number = (
            self.generate_account_number()
        )

        account.account_number = account_number

        self.accounts[account_number] = account

        return account

    # --------------------------------------------------------
    # Get Account
    # --------------------------------------------------------

    def get_account(self, account_number):

        if account_number not in self.accounts:
            raise AccountNotFoundError(
                "Account not found."
            )

        return self.accounts[account_number]

    # --------------------------------------------------------
    # Transfer Money
    # --------------------------------------------------------

    def transfer(
        self,
        sender_number,
        receiver_number,
        amount
    ):

        sender = self.get_account(
            sender_number
        )

        receiver = self.get_account(
            receiver_number
        )

        sender.transfer(
            receiver,
            amount
        )

    # --------------------------------------------------------
    # Show All Accounts
    # --------------------------------------------------------

    def show_all_accounts(self):

        if not self.accounts:
            print("No accounts available.")
            return

        for account in self.accounts.values():
            account.display()

    # --------------------------------------------------------
    # Save Data
    # --------------------------------------------------------

    def save_data(self, filename):

        data = {
            "bank_name": self.name,

            "accounts": [
                account.to_dict()
                for account in self.accounts.values()
            ]
        }

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    # --------------------------------------------------------
    # Load Data
    # --------------------------------------------------------

    def load_data(self, filename):

        try:

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            self.accounts = {}

            for account_data in data["accounts"]:

                account = BankAccount(
                    account_data["owner"],
                    account_data["pin"],
                    account_data["balance"]
                )

                account.account_number = (
                    account_data["account_number"]
                )

                account.is_active = (
                    account_data["is_active"]
                )

                account.transactions = []

                for transaction_data in (
                    account_data["transactions"]
                ):

                    transaction = Transaction(
                        transaction_data[
                            "transaction_type"
                        ],
                        transaction_data[
                            "amount"
                        ],
                        transaction_data[
                            "balance_after"
                        ],
                        transaction_data[
                            "description"
                        ]
                    )

                    transaction.timestamp = (
                        transaction_data["timestamp"]
                    )

                    account.transactions.append(
                        transaction
                    )

                self.accounts[
                    account.account_number
                ] = account

        except FileNotFoundError:

            pass


# ============================================================
# Input Functions
# ============================================================

def get_amount():

    while True:

        try:

            amount = float(
                input("Enter amount: ")
            )

            if amount <= 0:
                print(
                    "Amount must be greater than zero."
                )
                continue

            return amount

        except ValueError:

            print(
                "Please enter a valid number."
            )


def get_pin():

    while True:

        pin = input(
            "Enter 4-digit PIN: "
        )

        if pin.isdigit() and len(pin) == 4:
            return pin

        print(
            "PIN must contain exactly 4 digits."
        )


# ============================================================
# Create Account
# ============================================================

def create_account(bank):

    print("\n===== CREATE ACCOUNT =====")

    owner = input(
        "Enter owner name: "
    ).strip()

    if not owner:
        print("Name cannot be empty.")
        return

    pin = get_pin()

    initial_balance = get_amount()

    account = bank.create_account(
        owner,
        pin,
        initial_balance
    )

    print("\nAccount created successfully!")

    print(
        f"Account Number: "
        f"{account.account_number}"
    )


# ============================================================
# Deposit
# ============================================================

def deposit_money(bank):

    try:

        number = input(
            "Enter account number: "
        )

        account = bank.get_account(number)

        pin = input(
            "Enter PIN: "
        )

        if not account.verify_pin(pin):

            print("Incorrect PIN.")
            return

        amount = get_amount()

        account.deposit(amount)

        print(
            "Deposit successful!"
        )

        print(
            f"New balance: "
            f"${account.balance:.2f}"
        )

    except BankError as error:

        print(f"Error: {error}")


# ============================================================
# Withdraw
# ============================================================

def withdraw_money(bank):

    try:

        number = input(
            "Enter account number: "
        )

        account = bank.get_account(number)

        pin = input(
            "Enter PIN: "
        )

        if not account.verify_pin(pin):

            print("Incorrect PIN.")
            return

        amount = get_amount()

        account.withdraw(amount)

        print(
            "Withdrawal successful!"
        )

        print(
            f"New balance: "
            f"${account.balance:.2f}"
        )

    except BankError as error:

        print(f"Error: {error}")


# ============================================================
# Check Balance
# ============================================================

def check_balance(bank):

    try:

        number = input(
            "Enter account number: "
        )

        account = bank.get_account(number)

        pin = input(
            "Enter PIN: "
        )

        if not account.verify_pin(pin):

            print("Incorrect PIN.")
            return

        account.display()

    except BankError as error:

        print(f"Error: {error}")


# ============================================================
# Transfer
# ============================================================

def transfer_money(bank):

    try:

        sender = input(
            "Enter your account number: "
        )

        receiver = input(
            "Enter receiver account number: "
        )

        sender_account = bank.get_account(
            sender
        )

        pin = input(
            "Enter PIN: "
        )

        if not sender_account.verify_pin(pin):

            print("Incorrect PIN.")
            return

        amount = get_amount()

        bank.transfer(
            sender,
            receiver,
            amount
        )

        print(
            "Transfer successful!"
        )

        print(
            f"New balance: "
            f"${sender_account.balance:.2f}"
        )

    except BankError as error:

        print(f"Error: {error}")


# ============================================================
# Transaction History
# ============================================================

def transaction_history(bank):

    try:

        number = input(
            "Enter account number: "
        )

        account = bank.get_account(number)

        pin = input(
            "Enter PIN: "
        )

        if not account.verify_pin(pin):

            print("Incorrect PIN.")
            return

        account.show_transactions()

    except BankError as error:

        print(f"Error: {error}")


# ============================================================
# Change PIN
# ============================================================

def change_pin(bank):

    try:

        number = input(
            "Enter account number: "
        )

        account = bank.get_account(number)

        old_pin = input(
            "Enter old PIN: "
        )

        new_pin = get_pin()

        account.change_pin(
            old_pin,
            new_pin
        )

        print(
            "PIN changed successfully!"
        )

    except BankError as error:

        print(f"Error: {error}")


# ============================================================
# Close Account
# ============================================================

def close_account(bank):

    try:

        number = input(
            "Enter account number: "
        )

        account = bank.get_account(number)

        pin = input(
            "Enter PIN: "
        )

        if not account.verify_pin(pin):

            print("Incorrect PIN.")
            return

        account.close_account()

        print(
            "Account closed successfully!"
        )

    except BankError as error:

        print(f"Error: {error}")


# ============================================================
# Main Program
# ============================================================

def main():

    bank = Bank(
        "Omar National Bank"
    )

    data_file = "bank_data.json"

    bank.load_data(data_file)

    while True:

        print("\n")
        print("=" * 55)
        print("          OMAR NATIONAL BANK")
        print("=" * 55)

        print("1. Create Account")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Check Balance")
        print("5. Transfer Money")
        print("6. Transaction History")
        print("7. Change PIN")
        print("8. Close Account")
        print("9. Show All Accounts")
        print("10. Save Data")
        print("0. Exit")

        print("=" * 55)

        choice = input(
            "Choose an option: "
        )

        if choice == "1":

            create_account(bank)

        elif choice == "2":

            deposit_money(bank)

        elif choice == "3":

            withdraw_money(bank)

        elif choice == "4":

            check_balance(bank)

        elif choice == "5":

            transfer_money(bank)

        elif choice == "6":

            transaction_history(bank)

        elif choice == "7":

            change_pin(bank)

        elif choice == "8":

            close_account(bank)

        elif choice == "9":

            bank.show_all_accounts()

        elif choice == "10":

            bank.save_data(data_file)

            print(
                "Data saved successfully!"
            )

        elif choice == "0":

            bank.save_data(data_file)

            print(
                "\nThank you for using "
                "Omar National Bank!"
            )

            break

        else:

            print(
                "Invalid choice."
            )


# ============================================================
# Run Program
# ============================================================

if __name__ == "__main__":
    main()
