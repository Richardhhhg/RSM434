# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import requests
from time import sleep

s = requests.Session()
s.headers.update({'X-API-key': 'YSW7JD5I'}) # API Key from YOUR RIT Client

def get_tick():
    resp = s.get('http://localhost:9999/v1/case')
    if resp.ok:
        case = resp.json()
        return case['tick'], case['status']

def get_bid_ask(ticker):
    payload = {'ticker': ticker}
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

def get_position():
    resp = s.get ('http://localhost:9999/v1/securities')
    if resp.ok:
        book = resp.json()
        return abs(book[0]['position']) + abs(book[1]['position']) + abs(book[2]['position'])
    
def get_position_ticker(ticker_id):
    resp = s.get('http://localhost:9999/v1/securities')
    if resp.ok:
        book = resp.json()
        return book[ticker_id]['position']

def get_time_sales(ticker):
    payload = {'ticker': ticker, 'limit': 1}
    resp = s.get ('http://localhost:9999/v1/securities/tas', params = payload)
    if resp.ok:
        book = resp.json()
        time_sales_book = [item["quantity"] for item in book]
        return time_sales_book

def get_news(): 
    resp = s.get ('http://localhost:9999/v1/news')
    if resp.ok:
        news_query = resp.json()

        return news_query 

def get_open_orders():
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
    QUANTITY = 750
    OFFSET = 8
    order_type = 'LIMIT'
    
    
    tick, status = get_tick()

    
    while status == 'ACTIVE':   
        position = get_position() # this thing always returns absolute value
        
        # time_and_sales = get_time_sales('AC')
        
        # news = get_news()
        tickers = ['CNR', 'RY', 'AC']
        
        if position < MAX_EXPOSURE:
            for i in range(len(tickers)):
                best_bid_price, best_ask_price = get_bid_ask(tickers[i])
                bid_ask_spread = best_ask_price - best_bid_price
                if bid_ask_spread >= 0.03:
                    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': tickers[i], 'type': order_type, 'quantity': QUANTITY, 'price': best_bid_price, 'action': 'BUY'})
                    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': tickers[i], 'type': order_type, 'quantity': QUANTITY, 'price': best_ask_price, 'action': 'SELL'})

        sleep(0.03)
            
        for i in range(len(tickers)):
            ticker_position = get_position_ticker(i)
            if ticker_position < 0:
                resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': tickers[i], 'type': 'MARKET', 'quantity': abs(ticker_position)/OFFSET, 'price': best_bid_price, 'action': 'BUY'})
            if ticker_position > 0:
                resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': tickers[i], 'type': 'MARKET', 'quantity': abs(ticker_position)/OFFSET, 'price': best_ask_price, 'action': 'SELL'})

        # resp = s.post('http://localhost:9999/v1/commands/cancel', params = {'all': 1})
        
        
        tick, status = get_tick()
    

if __name__ == '__main__':
    main()
