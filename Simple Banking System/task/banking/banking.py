import random
import os
import sqlite3


class Card:
    dict_cards = {}
    cur = None
    conn = None

    def __init__(self):
        self.card_number = None
        self.pin = None
        self.balance = 0
        self.login = False

    @classmethod
    def create_db(cls):
        Card.conn = sqlite3.connect("card.s3db")
        Card.cur = Card.conn.cursor()
        Card.cur.execute(
            '''CREATE TABLE IF NOT EXISTS card(id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)''')
        Card.conn.commit()

    def check_balance(self):
        res = Card.cur.execute(f"SELECT balance FROM card WHERE number = {self.card_number}")
        print(res.fetchone()[0])

    def log_out(self):
        self.login = False
        print("You have successfully logged out!")

    def card_info(self):
        print(f'''Your card has been created
Your card number:
{self.card_number}
Your card PIN:
{self.pin}''')

    def create(self):
        min_ = 0
        max_ = 999999999
        account_id = str(random.randint(min_, max_))
        Card.cur.execute(F"INSERT INTO card ('id') VALUES ({account_id})")
        Card.conn.commit()
        account_id = "400000" + (len(str(max_)) - len(account_id)) * '0' + str(account_id)
        cs = self.check_luhn(account_id)

        if cs == '10':
            cs = '0'
        self.card_number = ''.join((account_id, cs))

        max_ = 9999
        pin = str(random.randint(min_, max_))
        self.pin = (len(str(max_)) - len(pin)) * '0' + pin
        if self.card_number not in Card.dict_cards:
            Card.dict_cards[self.card_number] = self.pin
        Card.cur.execute(F"INSERT INTO card ('number', 'pin') VALUES ({self.card_number}, {self.pin})")
        Card.conn.commit()
        Card.card_info(self)

    def log_in(self):
        number = str(input('Enter your card number:\n'))
        pin = str(input('Enter your PIN:\n'))
        if number in Card.dict_cards and Card.dict_cards[number] == pin:
            self.login = True
            self.card_number = number
            print("You have successfully logged in!")
        else:
            print("Wrong card number or PIN!")

    def add_income(self):
        income = input("Enter income:\n")
        Card.cur.execute(f"UPDATE card SET balance = balance + {income} WHERE number = {self.card_number}")
        Card.conn.commit()
        print("Income was added!")

    @staticmethod
    def check_luhn(num):
        luhn_account_id = list(map(int, num))
        for i in range(0, len(luhn_account_id), 2):
            luhn_account_id[i] *= 2
            if luhn_account_id[i] > 9:
                luhn_account_id[i] -= 9
        cs = str(10 - sum(luhn_account_id) % 10)
        return cs

    def transfer(self):
        print("Transfer")
        card_transfer = str(input("Enter card number:\n"))
        if card_transfer == self.card_number:
            print("You can't transfer money to the same account!")
        elif card_transfer in Card.dict_cards:
            sum_transfer = int(input("Enter how much money you want to transfer:\n"))
            res = Card.cur.execute(f"SELECT balance FROM card WHERE number = {self.card_number}")
            if res.fetchone()[0] < sum_transfer:
                print("Not enough money!")
            else:
                Card.cur.execute(
                    f"UPDATE card SET balance = balance - {sum_transfer} WHERE number = {self.card_number}")
                Card.conn.commit()
                Card.cur.execute(f"UPDATE card SET balance = balance + {sum_transfer} WHERE number = {card_transfer}")
                Card.conn.commit()
                print("Success!")
        elif self.check_luhn(card_transfer[:-1]) != card_transfer[-1]:

            print("Probably you made a mistake in the card number. Please try again!")
        else:
            print("Such a card does not exist.")

    def close_account(self):
        Card.cur.execute(f"DELETE FROM card WHERE number = {self.card_number}")
        Card.conn.commit()


def main():
    def action(num, in_out):
        actions_1 = {1: card.create, 2: card.log_in}
        actions_2 = {1: card.check_balance, 2: card.add_income,
                     3: card.transfer, 4: card.close_account, 5: card.log_out}
        if in_out:
            return actions_2.get(num)()
        return actions_1.get(num)()

    card = Card()
    card.create_db()

    running = True
    while running:
        if card.login:
            message = '''1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit'''
            scenario = True
        else:
            message = '''1. Create an account\n2. Log into account\n0. Exit'''
            scenario = False
        print(message)

        num_act = int(input())
        print()
        if num_act == 0:
            print("Bye!")
            break
        action(num_act, scenario)
        print()


if __name__ == "__main__":
    main()
