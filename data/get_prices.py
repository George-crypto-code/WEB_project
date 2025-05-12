import yfinance as yf
from pycoingecko import CoinGeckoAPI
from xml.etree import ElementTree
import requests
from datetime import datetime


def get_stock_price(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")
    if data.empty:
        return -1
    last_price = data['Close'].iloc[-1]
    return float(last_price)


def get_cbr_currency_rate(currency_code="USD"):
    today = datetime.now().strftime("%d/%m/%Y")
    url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={today}"
    response = requests.get(url)
    response.raise_for_status()
    root = ElementTree.fromstring(response.content)
    for valute in root.findall("Valute"):
        char_code = valute.find("CharCode").text
        if char_code == currency_code:
            value = valute.find("Value").text.replace(",", ".")
            return float(value)


def get_crypto_price(coin_id):
    vs_currency = "usd"
    cg = CoinGeckoAPI()
    price_data = cg.get_price(ids=coin_id, vs_currencies=vs_currency)
    if price_data:
        price = price_data[coin_id.lower()][vs_currency]
        return float(price)
