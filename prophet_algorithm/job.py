import logging
import os
from time import time
from datetime import datetime
import pandas as pd
from fbprophet import Prophet
from redistimeseries.client import Client

MSEC=1
SEC=MSEC*1000
MIN=60*SEC
HOUR=60*MIN
DAY=24*HOUR

def predict(host,port,t0):
    connection=Client(host=host,port=port)
    keys=['yhat','yhat_upper','yhat_lower','trend','trend_upper','trend_lower','daily','daily_lower','daily_upper']
    #flush old predictions
    for k in keys:
        try:
            connection.delete(k)
        except:
            logging.warn('Error Deleting keys')
            raise
            pass
    # create keys for storing the result
    for k in keys:
        try:
            connection.create(k,retention_msecs=7*DAY)
        except:
            pass

    # read data from timeseries structure
    data=connection.range("Temperature",
                from_time=0,
                to_time=-1,
                bucket_size_msec=60*5, # In Seconds NOT milliseconds
                aggregation_type='avg')
    # clean the data for the algorithm to run
    time,value=zip(*data)
    time=[datetime.fromtimestamp(x) for x in time]
    df=pd.DataFrame(dict(ds=time,y=value))
    m = Prophet(changepoint_prior_scale=0.02,interval_width=.95).fit(df)
    future = m.make_future_dataframe(periods=48, freq='H',include_history = True)
    fcst = m.predict(future)
    fcst=fcst.set_index('ds')
    # send data to redistimeseries struct

    # yhat_upper=fcst['yhat_upper'].values()
    # yhat_lower=fcst['yhat_lower'].values()
    def send(key):
        time=fcst.index.values
        time=[int(x.astype('uint64') / 1e9) for x in time]
        yhat=fcst[key].values
        yhat=[x.astype(float) for x in yhat]
        out=[(key,time,value) for time,value in zip(time,yhat)]
        connection.madd(out)
    [send(k) for k in keys]

