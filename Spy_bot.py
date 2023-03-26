import time
import telebot
from telebot import types

import json
import random
import requests

from bs4 import BeautifulSoup as bs

from binance import BinanceApi

from binance_wallet_tracker import BinanceWalletTracker

from binance_wallet_tracker.forms import WalletTrackerForm

from binance_wallet_tracker.functions.api import BinanceApiFunctions

token = "" # Replace with your own Telebot token
chat_id = "" # Get from Telegram by long-pressing the profile of your bot
wallet_address = "" # Replace with the address you want to track
list_of_tracked = [wallet_address]

bot = telebot.TeleBot(token)

def check_if_added(address):
    global list_of_tracked
    if address not in list_of_tracked:
        list_of_tracked.append(address)
    else:
        chat_text = f"Address {address} is already being tracked"
        bot.send_message(chat_id, chat_text)

def start_tracking(address):
    global list_of_tracked
    global wallet_address
    if address not in list_of_tracked:
        list_of_tracked.append(address)
    else:
        chat_text = f"The address {address} is already being tracked. It cannot be removed from the list."
        bot.send_message(chat_id, chat_text)

def reset_tracking(address):
    global list_of_tracked
    if address in list_of_tracked:
        list_of_tracked.remove(address)
    else:
        chat_text = f"Address {address} is not being tracked"
        bot.send_message(chat_id, chat_text)

def start_bot(initial_chat=True):
    if initial_chat:
        if wallet_address and list_of_tracked:
            bot.send_message(chat_id, f"Wallet {wallet_address} is already being tracked. Would you would like to track a new address?.")
                    bot.send_message(chat_id, f"Enter the address you would like to track: ")
        wallet_address = input()
        bot.send_message(chat_id, f"Adding the following address to the list of tracked addresses: {wallet_address}")
        start_tracking(wallet_address)
        bot.send_message(chat_id, f"Successfully added {wallet_address} to the list of tracked addresses")
        process_transaction(wallet_address)

else:
    for message in bot.message_list(chat_id):
        if message.text == "start":
            bot.send_message(chat_id, "Which address do you want to start tracking?")
            wallet_address = input()
            bot.send_message(chat_id, f"{wallet_address} is being added to the list of tracked addresses")

        if message.text == "list":
            chat_text = "Tracked Addresses:"
            for address in list_of_tracked:
                chat_text += address + '\n'
            bot.send_message(chat_id, chat_text)

        if message.text == "unlist":
            check_if_added(message.text)

        if message.text == "reset":
            for address in list_of_tracked:
                if address in WalletTrackerForm(bot):
                    start_tracking(message.text)
                else:
                    reset_tracking(message.text)

        if message.text == "pause":
            bot.send_message(chat_id, "Tracking has been paused.")
            start_tracking(wallet_address)
        elif message.text == "resume":
            bot.send_message(chat_id, "Tracking has been resumed.")
        elif message.text == "help":
            bot.send_message(chat_id, "You can use the following commands: start, list, unlist, pause, resume, help")

if name == 'main':
start_bot(initial_chat=True)

# Process all transactions for a given address
def process_transactions(wallet_address, start_point):
    self.is_loading = True
    while self.is_loading:
        response = self.binance_api.get_all_transactions(wallet_address, start_point)
        # Check if the response is not ready yet
        if not response:
            print(f"Request to get transactions data for {wallet_address} failed. Waiting for 2 seconds before trying again.")
            time.sleep(2)
            self.is_loading = True
            continue

        # Check if the response is empty
        if not response and self.is_loading:
            print(f"Request to get transactions data for {wallet_address} failed. Exiting process_transactions.")
            return

        # Check if the response has data for the given start_point
        if len(response.data.results) <= start_point:
            print(f"Could not get transactions data for {wallet_address}, exiting process_transactions.")
            return

        # If we reached this point, we have all the transactions data for the specified start_point and it's safe to proceed
        self_update = 0
        if start_point == 0:
            # Get the first address to display and remove it from the list of tracked addresses
            first_address = next(self.list_of_tracked)
            self.list_of_tracked.pop(0)
            # Check if data has been retrieved for this address
            if len(response.data.results) <= 0:
                print(f"Could not get transactions data for {first_address}, exiting process_transactions.")
                return
        
        for transaction_hash, transaction_dict in response.data.results:
            try:
                tx = self.binance_api.get_transaction_details(transaction_dict, start_point)
            exceptException as e:
                print(f"An error occurred while trying to retrieve the details of transaction {transaction_hash}.")

                break
            except Exception as e:
                print(f"An error occurred while trying to parse the transaction data for transaction {transaction_hash}.")
            if tx is None:
                print(f"Transaction {transaction_hash} returned an empty response.")
            else:
                # Check if the transaction is a transfer to this address, if not ignore it
                if 'destination' in tx and tx['destination'] == wallet_address:
                    transaction_json = tx_to_trx_json(tx)
                    transaction_json_list.append(transaction_json)  # Add the transaction to the list for display
                    self_update += 1
                    if self_update % 1000 == 0:  # Only update the display every 1000 transactions
                        self.display_trx_data()

        if self_update % 5000 == 0:  # Only send messages every 5000 transactions, to conserve API requests
            print(f"Displayed {self_update/1000} transactions out of {len(response.data.results)} ({self_update/5000:.0f}%)")
            self.is_loading = False
            time.sleep(2)

            self.check_if_added(list_of_tracked)  # Check if this address is being tracked
            if list_of_tracked and wallet_address not in list_of_tracked:
                list_of_tracked.append(wallet_address)
            if not list_of_tracked:
                print(f"Address {wallet_address} is not being tracked. Would you like to add it to the list of tracked addresses?")
                wallet_address = input()
                list_of_tracked.append(wallet_address)
            if list_of_tracked:
                message_to_send = f"Added the following address to the list of tracked addresses {list_of_tracked}."
                bot.send_message(chat_id, message_to_send)
            elif wallet_address in list_of_tracked:
                print(f"The address {wallet_address} is already being tracked. Updating display...")
                bot.send_message(chat_id, f"Tracked addresses: {list_of_tracked}")
                for item in transaction_json_list:
                    send_trx_json(item)
            else:
                print(f"Address {wallet_address} is not being tracked. Exiting process_transactions.")
                return

if __name__ == '__main__':
    process_transactions(wallet_address, start_point)