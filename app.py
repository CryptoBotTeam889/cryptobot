import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import mplfinance as mpf
import streamlit as st
import seaborn as sns
from datetime import datetime, timedelta
import requests
from cryptobot.brokers.enums import Intervals, Symbols

BASE_API_URL = "https://cryptobot-889-amz3m5pjwa-ew.a.run.app"
# THRESHOLD =.517037
THRESHOLD =.517039
INITIAL_INVEST=10000
DAYS_CANDLES=30
# candles=get_candles(Symbols.ETHUSDT, Intervals.ONE_HOUR, datetime.now()-timedelta(days=DAYS_CANDLES), datetime.now())

def get_candles(
    symbol: Symbols, interval: Intervals, start_time: datetime, end_time: datetime
):
    response = requests.get(
        BASE_API_URL + "/candles",
        params=dict(
            symbol=symbol.value,
            interval=interval.value,
            start_time=round(start_time.timestamp()),
            end_time=round(end_time.timestamp()),
        ),
    ).json()
    return response

@st.cache
def candles():
    candles=get_candles(Symbols.ETHUSDT, Intervals.ONE_HOUR, datetime(2022 , 5 , 1), datetime.now())
    df = pd.DataFrame(candles)
    df.open_time = df.open_time.apply(lambda x: datetime.utcfromtimestamp(x/1000))
    return df
candles=candles()

def predict(
    symbol: Symbols, interval: Intervals, start_time: datetime, end_time: datetime
):
    response = requests.get(
        BASE_API_URL + "/predict-range",
        params=dict(
            symbol=symbol.value,
            interval=interval.value,
            init=round(start_time.timestamp()),
            end=round(end_time.timestamp()),
        ),
    ).json()
    return response

@st.cache
def prediction():
    prediction=predict(Symbols.ETHUSDT, Intervals.ONE_HOUR, datetime(2022 , 5 , 1), datetime.now())
    prediction=pd.DataFrame(prediction)
    return prediction
prediction=prediction()

def create_df_stock(candles, prediction):
    df_stock = candles[["open_time","open","close"]]
    df_stock["symbol"] = prediction["predictions"].apply(lambda x: 0 if x <=THRESHOLD else 1)
    df_stock["USD"] = 0
    df_stock["ETH"] = 0
    df_stock.dropna(inplace=True)
    df_stock.reset_index(inplace=True)
    for index,row in df_stock.iterrows():
        if index == 0:
            df_stock.loc[index,'USD'] = INITIAL_INVEST
        else:
            df_stock.loc[index,'USD'] = df_stock.loc[index-1,'USD'] - (df_stock.loc[index,'symbol']*df_stock.loc[index-1,'USD'] - (1-df_stock.loc[index,'symbol'])*(df_stock.loc[index-1,'ETH']*df_stock.loc[index-1,'close']))
            df_stock.loc[index,'ETH'] = df_stock.loc[index-1,'ETH'] - ((1-df_stock.loc[index,'symbol'])*df_stock.loc[index-1,'ETH'] - df_stock.loc[index,'symbol']*(df_stock.loc[index-1,'USD']/df_stock.loc[index-1,'close']))
    df_stock["TOTAL_VALUE_IN_USD"] = df_stock["USD"] + df_stock["ETH"]*df_stock["close"]
    df_stock[["USD","TOTAL_VALUE_IN_USD"]] = df_stock[["USD","TOTAL_VALUE_IN_USD"]].applymap(lambda x: round(x,1))
    df_stock.set_index("open_time")
    return df_stock

df_stock = create_df_stock(candles,prediction)

CSS = """
h1 {
    color: red;
}
.stApp {
    background-image: url(https://img.freepik.com/vector-gratis/fondo-tecnologia-digital-abstracto-particulas-rojas_1017-23148.jpg?t=st=1654985006~exp=1654985606~hmac=f6232ddec6474cf502b77986e126d907acdcc9d0820bedebdf10909410b43a88&w=996);
    background-size: cover;
}
"""
st.write(f'<style>{CSS}</style>', unsafe_allow_html=True)

st.markdown("""
            ##             CRYPTOBOT
            """
            )

def get_select_box_data():

        return pd.DataFrame({
          'Pair List': ["ETHEREUM (ETHUSDT)",
                        "BITCOIN (BTCUSDT)",
                        "TETHER (THETAUSDT)"]
        })

box_data = get_select_box_data()

st.selectbox('Select a Currency to operate (in USD)', box_data['Pair List'])


st.markdown("""
            ### HISTORICAL CANDLESTICKS
            (WITH MOVING AVERAGES AND BUY/SELL VOLUME)
            """
            )

data = pd.DataFrame({
          'first column': list(range(-10, -251, 10)),
        'second column': np.arange(-10, -251, 10)
        })

line_count = st.slider('Select the hour range to show in plot', 20, -250, -1)
df_plot = candles[["open_time","open","high","low","close","volume"]].set_index("open_time")
# df_plot["symbol"] = (df_plot.close - df_plot.open).apply(lambda x: 0 if x <=0 else 1)
df_plot = df_plot.head(line_count)

def symbol_overzero(symbol,price):
    signal   = []
    previous = 1
    for date,value in symbol.iteritems():
        if value > 0 and previous <= 0:
            signal.append(price[date]*0.98)  # distancia entre la vela y el triangulo
        else:
            signal.append(np.nan)
        previous = value
    return signal

def symbol_abovezero(symbol,price):
    signal   = []
    previous = 1
    for date,value in symbol.iteritems():
        if value == 0 and previous != 0:
            signal.append(price[date]*1.02)
        else:
            signal.append(np.nan)
        previous = value
    return signal

# low_signal = symbol_abovezero(df_plot['symbol'], df_plot['close'])
# high_signal = symbol_overzero(df_plot['symbol'], df_plot['close'])

# apds = [
#        mpf.make_addplot(high_signal,type='scatter',markersize=50,marker='^', color='green'),
#        mpf.make_addplot(low_signal,type='scatter',markersize=50,marker='v', color='red')
#       ]

# mpf.plot(df_plot,addplot=apds,style='yahoo', type="candlestick" ,volume=True,mav=(20,50,100))
# mpf.plot(df_plot, style='yahoo', type="candlestick" ,volume=True,mav=(20,50,100))

st.set_option('deprecation.showPyplotGlobalUse', False)

#addplot=apds para agregar indicadores en triángulos
# fig = mpf.plot(df_plot,addplot=apds,style='yahoo', type="candlestick" ,volume=True,mav=(20,50,100))
fig = mpf.plot(df_plot,style='yahoo', type="candlestick" ,volume=True,mav=(20,50,100))
st.pyplot(fig)

st.markdown("""
            ### INITIAL AND END PERIOD VALUES
            """
            )

col1, col2 = st.columns(2)
col1.metric("ETC PERIOD OPEN", df_plot["open"][0])
col2.metric("ETC PERIOD CLOSE", df_plot["close"][-1],"{:.2%}".format((df_plot["close"][-1]-df_plot["open"][0])/df_plot["open"][0]))

# predictor = CryptoPredictor().predict(Symbols.ETHUSDT, datetime.now(), Intervals.ONE_HOUR)

#if st.button('Predict next period buy/sell order'):
    # print is visible in the server output, not in the page

    #st.write('Prediction')


st.markdown("""
            ### HOW CRYPTOBOT WOULD HAVE WORKED IN THE LAST 30 DAYS ?
            """
            )

number = st.number_input('Invest Simulator')

# df_stock = candles[["open_time","open","close"]]
# prediction.columns=["symbol_predicted"]
# df_stock["symbol"] = prediction["symbol_predicted"].apply(lambda x: 0 if x <=THRESHOLD else 1).to_list()
# df_stock["symbol"] = 1   Para estrategia de HOLD

INITIAL_INVEST=number

df_stock["USD"] = 0
df_stock["ETH"] = 0

df_stock.dropna(inplace=True)
df_stock.reset_index(inplace=True)

for index,row in df_stock.iterrows():

    if index == 0:
        df_stock.loc[index,'USD'] = INITIAL_INVEST

    else:
        df_stock.loc[index,'USD'] = df_stock.loc[index-1,'USD'] - (df_stock.loc[index,'symbol']*df_stock.loc[index-1,'USD'] - (1-df_stock.loc[index,'symbol'])*(df_stock.loc[index-1,'ETH']*df_stock.loc[index-1,'close']))
        df_stock.loc[index,'ETH'] = df_stock.loc[index-1,'ETH'] - ((1-df_stock.loc[index,'symbol'])*df_stock.loc[index-1,'ETH'] - df_stock.loc[index,'symbol']*(df_stock.loc[index-1,'USD']/df_stock.loc[index-1,'close']))

df_stock["TOTAL_VALUE_IN_USD"] = df_stock["USD"] + df_stock["ETH"]*df_stock["close"]
df_stock[["USD","TOTAL_VALUE_IN_USD"]] = df_stock[["USD","TOTAL_VALUE_IN_USD"]].applymap(lambda x: round(x,1))

df_stock.set_index("open_time")


investment_result = df_stock["TOTAL_VALUE_IN_USD"][len(df_stock["TOTAL_VALUE_IN_USD"])-1] - number

st.markdown("""
            ### HISTORICAL SIMULATION OF INVESTMENT (IN USD)
            """
            )

st.line_chart(df_stock["TOTAL_VALUE_IN_USD"])

col1, col2 = st.columns(2)
col1.metric("USING CRYPTOBOT, YOUR RESULT WOULD HAVE BEEN:", round(investment_result,3),"{:.2%}".format((investment_result/number)))

if st.button('Deposit funds in  wallet'):
    # print is visible in the server output, not in the page
    st.write("Scan QR to connect with wallet")
    st.image("cryptobot/data/QR.png")
