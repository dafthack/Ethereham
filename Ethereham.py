from brownie import *
from itertools import count
from click import style
from eth_utils import decode_hex
from time import sleep
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--startingblock', type=int, required=False, default=13004800)
parser.add_argument('-a', '--ethereumaddress', type=str, required=False)
parser.add_argument('-l', '--startfromlatest', dest='latest', action='store_true', required=False)
parser.add_argument('-t', '--scanalltransactions', dest='scan', action='store_true', required=False)

parser.set_defaults(latest=False)
args = parser.parse_args()

start_at_latest = args.latest
start_block = args.startingblock
eth_address = args.ethereumaddress
scan_all = args.scan

network.connect('mainnet')

if start_at_latest == True:
    print("The startfromlatest flag was specified. Overriding startingblock param and scanning from latest block")
    start_block = web3.eth.block_number

if scan_all == True:
    print("Extracting input data from all transactions starting at block number " + str(start_block))
else:
    print("Extracting input data for account " + eth_address + " starting at block number " + str(start_block))

print("---------------------------------------------------------")



def get_message(tx):
    try:
        return decode_hex(tx.input).decode('utf-8')
    except UnicodeDecodeError:
        return style('unintelligible', dim=True)


for n in count(start_block):
    while n > web3.eth.block_number:
        sleep(1)

    if n % 100 == 0 and n < web3.eth.block_number:
        print(style(f'{web3.eth.block_number - n:,d} blocks remaining', dim=True))
    block = web3.eth.get_block(n, True)
    
    if scan_all == True:
        for tx in block.transactions:
            message = get_message(tx)
            if message is None:
                continue
            
            if "unintellig" in message or message == '':
                continue
            else:
                print("---------------------------------------------------------")
                hash = (tx.hash).hex()
                print("Transaction Hash: " + str(hash))
                print(
                    f'[{n:,}]',
                    style(f"{tx['from'][:10]} says:", fg='green'),
                    message,
                )
            print("---------------------------------------------------------")
    else:
        for tx in block.transactions:
            if eth_address not in [tx['from'], tx.to]:
                continue
            message = get_message(tx)
            if message is None:
                continue
            print("---------------------------------------------------------")
            hash = (tx.hash).hex()
            print("Transaction Hash: " + str(hash))
            print(
                f'[{n:,}]',
                style(f"{tx['from'][:10]} says:", fg='green' if tx['from'] == eth_address else 'yellow'),
                message,
            )
            print("---------------------------------------------------------")
