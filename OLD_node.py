from uuid import uuid4

from index import Blockchain
from utility.verification import Verification
from wallet import Wallet

class Node:
    def __init__(self):
        # self.wallet.public_key = str(uuid4())
        self.wallet = Wallet()
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key)

    def get_transaction_value(self):
        tx_recipient = input('Enter the recipeint of the transaction: ')
        tx_amount = float(input('Your transaction amount please: '))
        return (tx_recipient, tx_amount)

    def get_user_choice(self):
        user_choice = int(input("Your choice: "))
        return user_choice


    def print_blockchain_elements(self):
        for block in self.blockchain.chain:
            print('Outputing Block')
            print(block)

    def listen_for_input(self):
        while True:
            print('Please choose')
            print('1: Add a new transaction')
            print('2: Print blockchain')
            print('3: Quit')
            print('4: Verify all transaction')
            print('5: Mine a new block')
            print('6: Create wallet')
            print('7: Load wallet')
            print('8: Save wallet')
            user_choice = self.get_user_choice()
            if user_choice == 1:
                tx_data = self.get_transaction_value()
                tx_recipient, tx_amount = tx_data
                signature = self.wallet.sign_transaction(self.wallet.public_key, tx_recipient, tx_amount)
                if self.blockchain.add_transaction(tx_recipient, self.wallet.public_key, signature, amount=tx_amount):
                    print('Added transaction!')
                else:
                    print('Transaction failed!')
                print(self.blockchain.get_open_transactions())
            elif user_choice == 2:
                self.print_blockchain_elements()
            elif user_choice == 4:
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transactions are valid')
                else:
                    print('There are invalid transactions')
            elif user_choice == 3:
                break
            elif user_choice == 5:
                if not self.blockchain.mine_block():
                    print("Mining failed")
            elif user_choice == 6:
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == 7:
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == 8:
                self.wallet.save_keys()
            else:
                print('Invalid choice')
            if not Verification.verify_chain(self.blockchain.chain):
                print('Invalid blockchain!')
                break
            print('Balance of {}: {:6.2f}'.format(self.wallet.public_key, self.blockchain.get_balance()))


        print("Done!")


if __name__ == '__main__':
    node = Node()
    node.listen_for_input()