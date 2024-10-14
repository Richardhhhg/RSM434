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
    
    MAX_EXPOSURE_NET = 25000
    MAX_EXPOSURE_GROSS = 500000
    OFFSET = 8
    QUANTITY = 1000
    order_type = 'LIMIT'
    
    
    tick, status = get_tick()

    if status == "ACTIVE":
        # getting leases
        resp = s.post('http://localhost:9999/v1/leases', params={'ticker':"ETF-Creation"})
        resp = s.post('http://localhost:9999/v1/leases', params={'ticker':"ETF-Redemption"})
        resp = s.get('http://localhost:9999/v1/leases')
        sleep(2)
        leases = resp.json()
        lease_number_create = leases[0]['id']
        lease_number_redeem = leases[1]['id']
    
    while status == 'ACTIVE':   
        position = get_position() # this thing always returns absolute value
        
        tickers = ['RGLD', 'RFIN', 'INDX']
        
        # generic arbitrage
        if position < MAX_EXPOSURE_NET:
            for i in range(len(tickers)):
                best_bid_price, best_ask_price = get_bid_ask(tickers[i])
                bid_ask_spread = best_ask_price - best_bid_price
                if bid_ask_spread >= 0.03:
                    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': tickers[i], 'type': order_type, 'quantity': QUANTITY, 'price': best_bid_price, 'action': 'BUY'})
                    resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': tickers[i], 'type': order_type, 'quantity': QUANTITY, 'price': best_ask_price, 'action': 'SELL'})

        sleep(0.25)
        
        # ETF arbitrage:
        # if position < MAX_EXPOSURE_NET:
        #     bid_RGLD, ask_RGLD = get_bid_ask(tickers[0])
        #     bid_RFIN, ask_RFIN = get_bid_ask(tickers[1])
        #     bid_INDX, ask_INDX = get_bid_ask(tickers[2])
        #     diff_buy_ETF =  ask_INDX - ask_RGLD - ask_RFIN # how much it costs to buy ETF
        #     dff_sell_ETF = bid_INDX - bid_RFIN - bid_RGLD - 0.0375 # how much it costs to sell ETF
        #     # if can buy portfolio cheaper than index
        #     #   buy portfolio, sell index
        #     if diff_buy_ETF > 0.05:
        #         # buy ETF, sell things at ask
        #         resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': "INDX", 'type': order_type, 'quantity': QUANTITY, 'price': ask_INDX, 'action': 'BUY'})
        for i in range(len(tickers)):
            ticker_position = get_position_ticker(i)
            print(ticker_position)
            if i == 0:
                if ticker_position < 0:
                    # redeem ETF for ticker
                    resp = s.post('http://localhost:9999/v1/leases/' + str(lease_number_redeem), params={'from1':'INDX', 'quantity1':ticker_position, 
                                                                                                        'from2':'CAD', 'quantity2':int(ticker_position*0.0375)})
                if ticker_position > 0:
                    resp = s.post('http://localhost:9999/v1/leases/' + str(lease_number_create), params={'from1':tickers[i], 'quantity1':ticker_position, 
                                                                                                        'from2':tickers[1], 'quantity2':ticker_position})
            if i == 1:
                if ticker_position < 0:
                    # redeem ETF for ticker
                    resp = s.post('http://localhost:9999/v1/leases/' + str(lease_number_redeem), params={'from1':'INDX', 'quantity1':ticker_position, 
                                                                                                        'from2':'CAD', 'quantity2':int(ticker_position*0.0375)})
                if ticker_position > 0:
                    resp = s.post('http://localhost:9999/v1/leases/' + str(lease_number_create), params={'from1':tickers[i], 'quantity1':ticker_position, 
                                                                                                        'from2':tickers[0], 'quantity2':ticker_position})
            if i == 2:
                if ticker_position > 0:
                    # redeem ETF for ticker
                    resp = s.post('http://localhost:9999/v1/leases/' + str(lease_number_redeem), params={'from1':'INDX', 'quantity1':ticker_position, 
                                                                                                        'from2':'CAD', 'quantity2':int(ticker_position*0.0375)})
                if ticker_position < 0:
                    resp = s.post('http://localhost:9999/v1/leases/' + str(lease_number_create), params={'from1':tickers[0], 'quantity1':ticker_position, 
                                                                                                        'from2':tickers[1], 'quantity2':ticker_position})
        
        # market orders for final offset of inventory risk
        for i in range(len(tickers)):
            ticker_position = get_position_ticker(i)
            if ticker_position < 0:
                resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': tickers[i], 'type': 'MARKET', 'quantity': abs(ticker_position)/OFFSET, 'price': best_bid_price, 'action': 'BUY'})
            if ticker_position > 0:
                resp = s.post('http://localhost:9999/v1/orders', params = {'ticker': tickers[i], 'type': 'MARKET', 'quantity': abs(ticker_position)/OFFSET, 'price': best_ask_price, 'action': 'SELL'})
        
        tick, status = get_tick()
    

if __name__ == '__main__':
    main()
