from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from wallet import Wallet
from index import Blockchain

app = Flask(__name__)
CORS(app)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)


@app.route('/', methods=['GET'])
def get_ui():
    return send_from_directory('ui', 'node.html')

@app.route('/wallet', methods=['POST'])
def create_keys():
    global blockchain
    wallet.create_keys()
    if wallet.save_keys():
        blockchain = Blockchain(wallet.public_key)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Saving keys failed'
        }
        return jsonify(response), 500




@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key == None:
        response = {
            'message': 'No wallet set up'
        }
        return jsonify(response), 500
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found'
        }
        return jsonify(response), 400
    required_fields = ['recipient', 'amount']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data is missing'
        }
        return jsonify(response), 400
    signature = wallet.sign_transaction(wallet.public_key, values['recipient'], values['amount'])
    if blockchain.add_transaction(values['recipient'],wallet.public_key, signature, values['amount']):
        response = {
            'message': 'Adding transaction was successful',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': values['recipient'],
                'amount': values['amount'],
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Adding transaction failed'
        }
        return jsonify(response), 500


@app.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transactions), 200
    # if wallet.public_key == None:
    #     response = {
    #         'message': 'No wallet set up'
    #     }

@app.route('/wallet', methods=['GET'])
def load_keys():
    global blockchain
    if wallet.load_keys():
        blockchain = Blockchain(wallet.public_key)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'loading keys failed'
        }
        return jsonify(response), 500


@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        response = {
            'message': 'Balance loaded successfully',
            'funds': balance
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Loading balance failed',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500




@app.route('/mine', methods=['POST'])
def mine():
    block = blockchain.mine_block()
    if block != None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message': 'Block added successfully',
            'block': dict_block,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Adding a block failed',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
    return (jsonify(dict_chain), 200)




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)