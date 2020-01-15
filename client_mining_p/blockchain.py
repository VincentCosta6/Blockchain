import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.difficulty = 6

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash
        }

        self.current_transactions = []

        self.chain.append(block)

        # Reset the current list of transactions
        # Append the chain to the block
        # Return the new block
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It convertes the string to bytes.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # TODO: Create the block_string
        string_object = json.dumps(block, sort_keys=True).encode()

        # TODO: Hash this string using sha256
        raw_hash = hashlib.sha256(string_object)

        hex_hash = raw_hash.hexdigest()

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # TODO: Return the hashed block string in hexadecimal format
        return hex_hash

    @property
    def last_block(self):
        return self.chain[-1]

    def valid_proof(self, block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        # TODO

        guess = f"{block_string}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:self.difficulty] == ("0" * self.difficulty)


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['POST'])
def mine():
    # Run the proof of work algorithm to get the next proof

    # Forge the new Block by adding it to the chain with the proof

    data = request.get_json()

    print(data)

    if data['id'] != blockchain.last_block['index'] + 1:
        response = {
            'error': 'incorrect id',
            'help': 'block may have been mined already'
        }
        return jsonify(response), 406

    block_string = json.dumps(blockchain.last_block, sort_keys=True).encode()
    prev_hash = blockchain.hash(blockchain.last_block)

    if blockchain.valid_proof(block_string, data['proof']) is False:
        response = {
            'error': 'incorrect proof',
            'help': 'your proof of work was incorrect'
        }
        return jsonify(response), 406

    block = blockchain.new_block(data['proof'], prev_hash)

    response = {
        'new_block': block,
        'message': 'verified'
    }

    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'length': len(blockchain.chain),
        'chain': blockchain.chain
    }
    return jsonify(response), 200

@app.route('/last_block', methods=['GET'])
def last_block():
    response = {
        'last': blockchain.last_block,
        'difficulty': blockchain.difficulty
    }

    return jsonify(response), 200

@app.route('/difficulty', methods=['GET'])
def difficulty():
    response = {
        'difficulty': blockchain.difficulty
    }

    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)