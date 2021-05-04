import yfinance as yf
import pandas_datareader.data as web
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import plotly.express as px


def course_getter(currency: str, start: datetime):
    return web.DataReader(currency + '=X', 'yahoo', start=start)['Adj Close'][0]


def stocks_data_getter(tickers: list[str], start: datetime, end: datetime):
    stocks_data = pd.DataFrame(columns=tickers)
    for ticker in tickers:
        stocks_data[ticker] = yf.download(ticker, start, end)['Adj Close']
    return stocks_data.fillns(method='bfill').resample('M').last()


def ticker_monthly_buyer(stocks_data: pd.DataFrame, monthly_income: int, balance: int) -> pd.DataFrame:
    active_labels = []
    balance_labels = []
    for ticker in stocks_data.columns:
        active_label = 'active_' + str(ticker)
        active_labels.append(active_label)
        balance_label = 'balance_' + str(ticker)
        balance_labels.append(balance_label)
        # закупаем каждый месяц
        stocks_data[active_label] = monthly_income / stocks_data[ticker]

        # закупили индекс в начале
        stocks_data[active_label].iloc[0] = balance / stocks_data.iloc[0][ticker]

        # суммируем по каждому месяцу
        stocks_data[active_label] = stocks_data[active_label].cumsum()

        # переведём обратно в долоры
        stocks_data[balance_label] = stocks_data[active_label] * stocks_data[ticker]
    return stocks_data.drop(active_labels, axis=1)


def indices_plotter(stocks_data: pd.DataFrame, tickers: list[str]):
    stocks_data.plot(y=list(map(lambda x: 'balance_' + x, tickers)), figsize=(16, 9))


def get_credit_sum(percent: float, sum: float, initial_fee: float):
    pass


if __name__ == '__main__':
    st.title("Educational calculator")
    years_count = st.sidebar.selectbox("How many years would you like to calculate?", range(1, 6))
    end = datetime.today() - timedelta(days=1)
    start = end - timedelta(days=365*years_count)
    currencies = [
        "RUB",
        "USD",
        "GBP",
        "EUR",
    ]
    currency = st.sidebar.selectbox("Select your currency", currencies)
    course = course_getter(currency, start)
    balance = float(st.sidebar.text_input("Your current balance: ")) / course
    monthly_income = float(st.sidebar.text_input("Your monthly savings: ")) / course
    tickers = ['CIH', '^GSPC', '^IXIC']
    stocks_data = stocks_data_getter(tickers, start, end)
    stocks_data = ticker_monthly_buyer(stocks_data, monthly_income, balance)
    graph = px.line(stocks_data[map(lambda x: f"balance_{x}", currencies)])
    st.plotly_chart(graph)
