# -*- coding: utf-8 -*-
"""
This version slightly change the logics in main.
Consider:
1. close all positions and then kill all orders unfilled when there is only 15 seconds remaining.
2. should we accept the tender offers
3. Dynamically adjust the quantity traded.
"""
import requests
from time import sleep

s = requests.Session()
s.headers.update({'X-API-key': 'YSW7JD5I'}) # API Key from YOUR RIT Client

def get_tick():
    """
    The founction returns a tuple ('tick', 'status')(10, 'ACTIVE')
    case = {
    'name': 'ALGO2 v2',
    'period': 1,
    'tick': 10,
    'ticks_per_period': 300,
    'total_periods': 1,
    'status': 'ACTIVE',
    'is_enforce_trading_limits': False
    }
    """
    resp = s.get('http://localhost:9999/v1/case')
    if resp.ok:
        case = resp.json()
        return case['tick'], case['status']

def get_bid_ask(ticker):
    payload = {'ticker': ticker} # payload = {'ticker': 'AC'}
    resp = s.get ('http://localhost:9999/v1/securities/book', params = payload)
    if resp.ok:
        book = resp.json()
        bid_side_book = book['bids']
        ask_side_book = book['asks']
        
        bid_prices_book = [item["price"] for item in bid_side_book]
        ask_prices_book = [item['price'] for item in ask_side_book]
        
        best_bid_price = bid_prices_book[0]
        best_ask_price = ask_prices_book[0]
  
        return best_bid_price, best_ask_price

# def dynamic_quantity():
    """This function returns a Boolean. If all bid/ask orders can be filled, it returns True"""


def get_position():
    """
    This function returns a number, which shows my current position.（持仓情况）
    """
    resp = s.get ('http://localhost:9999/v1/securities')
    # The resp here is a list of dictionaries. 
    # If there are 3 stocks, there will be 3 items in the list.
    if resp.ok:
        book = resp.json()
        return abs(book[0]['position']) + abs(book[1]['position']) + abs(book[2]['position'])
    
def get_position_ticker(ticker_id):
    """
    Given the ticker_id(1,2,3), this function returns the corresponding position of the ticker.
    (特定股票持仓情况)
    """
    resp = s.get('http://localhost:9999/v1/securities')
    if resp.ok:
        book = resp.json()
        return book[ticker_id]['position']

def get_time_sales(ticker):
    """This function returns a list of 'quantity': [800.0, ..., 200.0] """
    payload = {'ticker': ticker, 'limit': 1}
    # payload = {'ticker': 'AC'}
    resp = s.get ('http://localhost:9999/v1/securities/tas', params = payload)
    if resp.ok:
        book = resp.json()
        # book is a list of dictionaries that contains all of the trades
        time_sales_book = [item["quantity"] for item in book]
        return time_sales_book

def get_news(): 
    """The function returns a list of dictionaries"""
    resp = s.get ('http://localhost:9999/v1/news')
    if resp.ok:
        news_query = resp.json()
    # news_query is a list of dictionaries including news_id, periods, headers...
    # news_query[0]
        return news_query 

def get_open_orders():
    """The function returns a tuple
    监控活跃的,尚未成交的orders"""
    resp = s.get ('http://localhost:9999/v1/orders')
    if resp.ok:
        orders = resp.json()
        buy_orders = [item for item in orders if item["action"] == "BUY"]
        sell_orders = [item for item in orders if item["action"] == "SELL"]
        return buy_orders, sell_orders

def get_order_status(order_id):
    resp = s.get ('http://localhost:9999/v1/orders' + '/' + str(order_id))
    if resp.ok:
        order = resp.json()
        return order['status']
    
def main():
    
    MAX_EXPOSURE = 25000
    QUANTITY = 500
    order_type = 'LIMIT'
    
    tick, status = get_tick()
    tickers = ['CNR', 'RY', 'AC']
    
    while status == 'ACTIVE':   
        
        for i in range(len(tickers)):
            position = get_position()
    
            if position < MAX_EXPOSURE:
            
                best_bid_price, best_ask_price = get_bid_ask(tickers[i])
                bid_ask_spread = best_ask_price - best_bid_price
                # This only works when there is a high volatility
                if bid_ask_spread >= 0.03: 
                    # compare the quantities to see if all orders can be filled
                    # adjust the quantity to optimize returns
                    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': tickers[i], 'type': order_type, 'quantity': QUANTITY, 'price': best_bid_price, 'action': 'BUY'})
                    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': tickers[i], 'type': order_type, 'quantity': QUANTITY, 'price': best_ask_price, 'action': 'SELL'})

                # pauses the code to give the passive orders a chance to trade before being cancelled
                sleep (0.25)

                # cancels any unfilled orders
                cancel_resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'ticker': tickers[i]})
        # tender offer?
        # sleep(0.25)
            
        # for i in range(len(tickers)):
        #     ticker_position = get_position_ticker(i)
        #     if ticker_position < 0:
        #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': tickers[i], 'type': 'MARKET', 'quantity': abs(ticker_position), 'price': best_bid_price, 'action': 'BUY'})
        #     if ticker_position > 0:
        #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': tickers[i], 'type': 'MARKET', 'quantity': abs(ticker_position), 'price': best_ask_price, 'action': 'SELL'})

        # resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'all': 1})
        
        
        tick, status = get_tick()

    # close all positions first and then kill all the orders
    # time remaining < 15 seconds
    

if __name__ == '__main__':
    main()

