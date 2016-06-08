'''
Created on 06.06.2016

@author: Jan
'''
import time

from siteconnector import * 
import feedofcsv




t_data = [] 
price_data = []
sma_ff = feedofcsv.Wmavrg(30)
sma_ff_data = []
sma_f = feedofcsv.Wmavrg(60)
sma_f_data = []
bollinger = feedofcsv.BollingerW(30)
bollinger_data = []

window = openBinaryoptionsDemoInChrome()  

ts0, price, balance = getcurrtimepricebalancedemo(window)

accdata = feedofcsv.AccData(balance)
buyoption(window, price=5,duration_pos=1)

running = True
oldprice = 0

while running:
    try:
        ts, price, balance = getcurrtimepricebalancedemo(window)
        if oldprice == price:
            time.sleep(0.25)
            continue
        oldprice = price
    except Exception as e:
        print e   
        time.sleep(0.1)
        continue
    print ts, price
    if ts is not None and price is not None:
        t_data.append(ts)
        price_data.append(price)
        sma_ff_data.append(sma_ff.update(ts,price))
        sma_f_data.append(sma_f.update(ts,price))
        bollinger_data.append(bollinger.update(ts,price))
        feedofcsv.Option.update(ts,accdata,price)  
        if ts - ts0 > 30: #start time 30sec
            maxval = max(sma_ff.samples_nonone)
            cnt = 0
            for e in sma_ff.samples_nonone:
                if e == maxval:
                    cnt +=1
            trendup = None
            if sma_ff_data[-1] > sma_f_data[-1]:
                trendup = True
            if sma_ff_data[-1] < sma_f_data[-1]:
                trendup = False
                                
            if  price >= maxval and len(accdata.portfolio) < 2 and not trendup:
                print ts, price, sma_ff_data[-1]
                print "buy"
                buyoption(window, up=False)
                feedofcsv.Option(ts, price, 60,accdata, up=False, price=100 )
            elif price >= maxval and len(accdata.portfolio) < 2 and trendup:
                print "dont by down in trend up"
                
                  
    time.sleep(0.25)