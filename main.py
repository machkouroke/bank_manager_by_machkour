import random
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
# database initialisation
cur.execute('''
CREATE TABLE IF NOT EXISTS card(
    id INTEGER PRIMARY KEY NOT NULL ,
    number TEXT,
    pin TEXT,
    balance INTEGER DEFAULT 0
);
''')


class Account:

    def __init__(self, account_number="", code="", solde=0, identifier="", checksum=""):
        self.account_number, self.code = account_number, code
        self.identifier, self.checksum = identifier, checksum
        self.solde = solde

    # This method allows you to check if an account already exists
    @staticmethod
    def already_exists(to_check):
        cur.execute("SELECT * FROM card WHERE number = ?", [to_check])
        existe = cur.fetchone()
        return existe is not None

    # This method allows a randomly generated code to be completed with a checksum that verifies the luhn algorithm.
    def luhn_complementor(self):
        luhn = list(self.account_number)
        luhn = list(map(int, luhn))
        for i in range(len(luhn)):
            if i % 2 == 0:
                luhn[i] *= 2
                if luhn[i] > 9:
                    luhn[i] -= 9
        somme = sum(luhn)
        return str(abs(somme % -10))

    # This method checks if a card number is compatible with the luhn algorithm.
    @staticmethod
    def luhn_verificator(number_to_check):
        luhn = list(number_to_check)
        luhn = list(map(int, luhn))
        for i in range(len(luhn)):
            if i % 2 == 0:
                luhn[i] *= 2
                if luhn[i] > 9:
                    luhn[i] -= 9
        somme = sum(luhn)
        return somme % 10 == 0

    # This method generates customer information
    def account_generator(self):
        unique = True
        # Loop to check if the created account is unique
        while unique:
            self.identifier = random.sample(range(9), 9)
            self.code = str(random.randint(0, 9999)).zfill(4)
            self.account_number = "400000" + ''.join(map(str, self.identifier))
            self.checksum = self.luhn_complementor()
            self.account_number += self.checksum
            if not self.already_exists(self.account_number):
                unique = False
        cur.execute('''INSERT INTO card (number, pin,balance) VALUES  (?, ?, ?);
               ''', (self.account_number, self.code, 0))
        conn.commit()
        print("\nYour card has been created")
        print("Your card number:")
        print(client.account_number)
        print("Your card PIN:")
        print(client.code)
        print()

    # Contains the instructions to allow login to the user
    def login(self):
        print("\nEnter your card number:")
        id_input = input()
        print("Enter your PIN")
        pin_input = input()
        print()
        right_information = False
        cur.execute(f'SELECT number, pin, balance FROM card WHERE (number = {id_input} and pin = {pin_input})')
        sucess_login = cur.fetchone()

        if sucess_login is not None:
            self = Account(id_input, pin_input, sucess_login[2])
            right_information = True
        if right_information:
            print('\nYou have successfully logged in!\n')
            while True:
                print('1. Balance')
                print('2. Add income')
                print('3. Do transfert')
                print('4. Close account')
                print('5. Log out')
                print('0. Exit')
                choice = input()
                if choice == '0':
                    print()
                    print("\nBye!\n")
                    exit()
                elif choice == '1':
                    print(f'\nBalance: {self.solde}\n')
                elif choice == '2':
                    print('\nEnter income:')
                    income = int(input())
                    cur.execute(f"UPDATE card SET balance = {income} + balance WHERE number = {self.account_number};")
                    conn.commit()
                    self.solde += income
                    print("Income was added!")
                elif choice == '3':
                    print("\nTransfer\nEnter card number:")
                    user_of_transfert = input()
                    if user_of_transfert == self.account_number:
                        print("You can't transfer money to the same account!")
                    elif not self.luhn_verificator(user_of_transfert):
                        print('Probably you made a mistake in the card number. Please try again!')
                    elif not self.already_exists(user_of_transfert):
                        print("Such a card does not exist")
                    else:
                        print('Enter how much money you want to transfert:')
                        sold_of_transfert = abs(int(input()))
                        if sold_of_transfert > self.solde:
                            print("Not enough money!")
                        else:
                            cur.execute(f'''
                                UPDATE card 
                                    SET balance = balance - {sold_of_transfert}
                                    WHERE number = {self.account_number};''')
                            cur.execute(f'''
                                UPDATE card 
                                    SET balance = balance + {sold_of_transfert}
                                    WHERE number = {user_of_transfert};''')
                            conn.commit()
                            self.solde -= sold_of_transfert
                            print('Sucess!\n')
                elif choice == '4':
                    cur.execute(f'DELETE FROM card WHERE number ={self.account_number}')
                    conn.commit()
                    print('\nThe account has been closed!\n')
                    break
                elif choice == '5':
                    print('\nYou have successfully logged out!\n')
                    break

        else:
            print('\nWrong card number or PIN!\n')


choice, client = '', Account()
while True:
    print('1. Create an account')
    print('2. Log into account')
    print('0. Exit')
    choice = input()
    if choice == '0':
        break
    elif choice == '1':
        client.account_generator()
    elif choice == '2':
        client.login()

print("\nBye!\n")
conn.close()
