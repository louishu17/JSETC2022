#!/usr/bin/env python3
# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py --test prod-like; sleep 1; done

from valbz import valbz_order
import argparse
from collections import deque
import time
import socket
import json
from utils import Dir, PriceHistory, do_tick, get_order_id, init
from pennying import PennyingStrategy
from bond import BondStrategy

# ~~~~~============== CONFIGURATION  ==============~~~~~
# Replace "REPLACEME" with your team name!
team_name = "shinerperch"

# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    args = parse_arguments()

    exchange = ExchangeConnection(args=args)

    # Store and print the "hello" message received from the exchange. This
    # contains useful information about your positions. Normally you start with
    # all positions at zero, but if you reconnect during a round, you might
    # have already bought/sold symbols and have non-zero positions.
    hello_message = exchange.read_message()
    print("First message from exchange:", hello_message)

    # Send an order for BOND at a good price, but it is low enough that it is
    # unlikely it will be traded against. Maybe there is a better price to
    # pick? Also, you will need to send more orders over time.
    exchange.send_add_message(
        order_id=1, symbol="BOND", dir=Dir.BUY, price=990, size=1
    )

    # Set up some variables to track the bid and ask price of a symbol. Right
    # now this doesn't track much information, but it's enough to get a sense
    # of the VALE market.
    vale_bid_price, vale_ask_price = None, None
    vale_last_print_time = time.time()

    history = PriceHistory()
    init()
    cancel_timer_dict = {}
    pennying_pairs = {}

    # Here is the main loop of the program. It will continue to read and
    # process messages in a loop until a "close" message is received. You
    # should write to code handle more types of messages (and not just print
    # the message). Feel free to modify any of the starter code below.
    #
    # Note: a common mistake people make is to call write_message() at least
    # once for every read_message() response.
    #
    # Every message sent to the exchange generates at least one response
    # message. Sending a message in response to every exchange message will
    # cause a feedback loop where your bot's messages will quickly be
    # rate-limited and ignored. Please, don't do that!
    while True:
        tick = do_tick()
        message = exchange.read_message()
        # Some of the message types below happen infrequently and contain
        # important information to help you understand what your bot is doing,
        # so they are printed in full. We recommend not always printing every
        # message because it can be a lot of information to read. Instead, let
        # your code handle the messages and just print the information
        # important for you!
        if message["type"] == "close":
            print("The round has ended")
            break
        elif message["type"] == "error":
            print(message)
        elif message["type"] == "reject":
            print(message)
        elif message["type"] == "fill":
            print(message)
            # If pennying position is filled, prevent other position from canceling
            id1 = message["order_id"]
            if id1 in pennying_pairs:
                id2 = pennying_pairs[id1]
                if id1 in cancel_timer_dict:
                    cancel_timer_dict.pop(id1)
                if id2 in cancel_timer_dict:
                    cancel_timer_dict.pop(id2)
        elif message["type"] == "ack":
            print(message)
        elif message["type"] == "book":

            # Update current market info with book
            history.update(message)

            # if message["symbol"] in ["VALE", "VALBZ"]:
            #     pass
            #     """"""
            #     sym = message["symbol"]
            #     last_vale = history.last_ba(sym) if sym == "VALBZ" message["buy"]
            #     other = "VALE" if m == "VALBZ" else "VALBZ"
            #     bid, ask = best_price("buy"), best_price("sell")

        bond_history_book = history.get("BOND")
        if bond_history_book:
            bond_buy_msgs = bond_history_book[-1]["buy"]
            bond_sell_msgs = bond_history_book[-1]["sell"]
            buy_orders, sell_orders = BondStrategy.bondStrategy(
                bond_buy_msgs, bond_sell_msgs)

            for b in buy_orders:
                exchange.send_add_message(**b)
            for s in sell_orders:
                exchange.send_add_message(**s)

        # pennying strat
        for sym in ["XLF"]:
            if tick % 20 != 0:
                break
            history_book = history.get_last(sym)
            if history_book:
                buy_orders, sell_orders, cancel_timers = PennyingStrategy.pennying_strategy(
                    sym, history_book["buy"], history_book["sell"]
                )
                if cancel_timers:
                    cancel_timer_dict.update(cancel_timers)
                    id1, id2 = cancel_timers.keys()
                    pennying_pairs[id1] = id2
                    pennying_pairs[id2] = id1

                for b in buy_orders:
                    exchange.send_add_message(**b)
                for s in sell_orders:
                    exchange.send_add_message(**s)

                for order_id, cancel_timer in dict(cancel_timer_dict).items():
                    c = cancel_timer.do_tick()
                    if c:
                        cancel_timer_dict.pop(order_id)
                        exchange.send_cancel_message(**c)

        # valbz orders
        if message["type"] == "book":
            orders, cancels = valbz_order(message, history, tick)
            for b in orders:
                print("valbz order: ", b["dir"])
                exchange.send_add_message(**b)
            for c in cancels:
                print("cancel orders: ", c)
                exchange.send_cancel_message(c)


class ExchangeConnection:
    def __init__(self, args):
        self.message_timestamps = deque(maxlen=500)
        self.exchange_hostname = args.exchange_hostname
        self.port = args.port
        self.exchange_socket = self._connect(
            add_socket_timeout=args.add_socket_timeout)

        self._write_message({"type": "hello", "team": team_name.upper()})

    def read_message(self):
        """Read a single message from the exchange"""
        message = json.loads(self.exchange_socket.readline())
        if "dir" in message:
            message["dir"] = Dir(message["dir"])
        return message

    def send_add_message(
        self, order_id: int, symbol: str, dir: Dir, price: int, size: int
    ):
        """Add a new order"""
        self._write_message(
            {
                "type": "add",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "price": price,
                "size": size,
            }
        )

    def send_convert_message(self, order_id: int, symbol: str, dir: Dir, size: int):
        """Convert between related symbols"""
        self._write_message(
            {
                "type": "convert",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "size": size,
            }
        )

    def send_cancel_message(self, order_id: int):
        """Cancel an existing order"""
        print({"type": "cancel", "order_id": order_id})
        self._write_message({"type": "cancel", "order_id": order_id})

    def _connect(self, add_socket_timeout):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if add_socket_timeout:
            # Automatically raise an exception if no data has been recieved for
            # multiple seconds. This should not be enabled on an "empty" test
            # exchange.
            s.settimeout(5)
        s.connect((self.exchange_hostname, self.port))
        return s.makefile("rw", 1)

    def _write_message(self, message):
        json.dump(message, self.exchange_socket)
        self.exchange_socket.write("\n")

        now = time.time()
        self.message_timestamps.append(now)
        if len(
            self.message_timestamps
        ) == self.message_timestamps.maxlen and self.message_timestamps[0] > (now - 1):
            print(
                "WARNING: You are sending messages too frequently. The exchange will start ignoring your messages. Make sure you are not sending a message in response to every exchange message."
            )


def parse_arguments():
    test_exchange_port_offsets = {"prod-like": 0, "slower": 1, "empty": 2}

    parser = argparse.ArgumentParser(description="Trade on an ETC exchange!")
    exchange_address_group = parser.add_mutually_exclusive_group(required=True)
    exchange_address_group.add_argument(
        "--production", action="store_true", help="Connect to the production exchange."
    )
    exchange_address_group.add_argument(
        "--test",
        type=str,
        choices=test_exchange_port_offsets.keys(),
        help="Connect to a test exchange.",
    )

    # Connect to a specific host. This is only intended to be used for debugging.
    exchange_address_group.add_argument(
        "--specific-address", type=str, metavar="HOST:PORT", help=argparse.SUPPRESS
    )

    args = parser.parse_args()
    args.add_socket_timeout = True

    if args.production:
        args.exchange_hostname = "production"
        args.port = 25000
    elif args.test:
        args.exchange_hostname = "test-exch-" + team_name
        args.port = 25000 + test_exchange_port_offsets[args.test]
        if args.test == "empty":
            args.add_socket_timeout = False
    elif args.specific_address:
        args.exchange_hostname, port = args.specific_address.split(":")
        args.port = int(port)

    return args


if __name__ == "__main__":
    # Check that [team_name] has been updated.
    assert (
        team_name != "REPLACEME"
    ), "Please put your team name in the variable [team_name]."

    main()
