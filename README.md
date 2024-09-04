# BTG Solutions - OTC Markets

Python library to access BTG OTC Markets.

## Installation

```bash
pip3 install btgsolutions-otcmarkets-python-client
```

## Examples

### Ticker Reference Data

```python
import btgsolutions_otcmarkets as otc
ref = otc.ReferenceData(api_key='API_KEY')
ref.get_ticker_data(tickers=['ZTEST01', 'ZTEST02'])
```

### Ticker Reference Data (All Tickers)

```python
import btgsolutions_otcmarkets as otc
ref = otc.ReferenceData(api_key='API_KEY')
ref.get_ticker_data()
```

### Ticker Pricing

```python
import btgsolutions_otcmarkets as otc
pricing = otc.Pricing(api_key='API_KEY')
pricing.get_ticker_price(ticker='ZTEST01', rate=6.51)
# pricing.get_ticker_rate(ticker='ZTEST01', price=1052.20)
```

### Top Of Book

```python
import btgsolutions_otcmarkets as otc
tob = otc.TopOfBook(api_key='API_KEY')
tob.get_top_of_book(ticker='ZTEST01')
```

### Top Of Book (All Tickers)

```python
import btgsolutions_otcmarkets as otc
tob = otc.TopOfBook(api_key='API_KEY')
tob.get_top_of_book()
```

### Risk Status

```python
import btgsolutions_otcmarkets as otc
risk = otc.Risk(api_key='API_KEY')
risk.risk_status_trader(investor_id='YOUR_INVESTOR_ID')
# risk.risk_status_investor(investor_id='YOUR_INVESTOR_ID')
```

### Market Data Stream

```python
import btgsolutions_otcmarkets as otc
mktdata = otc.MarketDataStream(api_key='API_KEY')
mktdata.run()
mktdata.subscribe(tickers=['ZTEST01'])
# mktdata.unsubscribe(tickers=['ZTEST01'])

## The following code is optional, it keeps the program running in a .py file:
# from time import sleep
# while True:
#   sleep(1)
```

### Order Entry - Create New Order

```python
import btgsolutions_otcmarkets as otc
order_entry = otc.OrderEntry(api_key='API_KEY', investor_id='YOUR_INVESTOR_ID')
order_entry.run()
order_entry.create_new_order(
    order_temp_id="123",
    ticker='ZTEST01',
    rate=6.22,
    qty=200,
    side='buy',
)

## The following code is optional, it keeps the program running in a .py file:
# from time import sleep
# while True:
#   sleep(1)
```

### Order Entry - Replace Order

```python
import btgsolutions_otcmarkets as otc
order_entry = otc.OrderEntry(api_key='API_KEY', investor_id='YOUR_INVESTOR_ID')
order_entry.run()
order_entry.replace_order(
    external_id="your-order-external-id",
    rate=6.30,
    qty=180,
)

## The following code is optional, it keeps the program running in a .py file:
# from time import sleep
# while True:
#   sleep(1)
```

### Order Entry - Cancel Order

```python
import btgsolutions_otcmarkets as otc
order_entry = otc.OrderEntry(api_key='API_KEY', investor_id='YOUR_INVESTOR_ID')
order_entry.run()
order_entry.cancel_order(
    external_id="your-order-external-id",
)

## The following code is optional, it keeps the program running in a .py file:
# from time import sleep
# while True:
#   sleep(1)
```
