'''
Created on 07.05.2016

@author: Jan

inspired by
http://binaryoptionschannel.com/most-reliable-60-seconds-strategy/
May 7th, 2014 by Tim Lanoue

TODO check numpy array or dequeue for speed improvement
tODO make pandas dataframe from csv for cleanup and improved usability (less ifcases to handle none values)


'''
            

import time 
import calendar

import numpy as np
import pandas
import matplotlib.pyplot as plt

import cPickle
import feedofcsv
from numpy import sign

import datetime as datetimemodule
import matplotlib.dates as md


filename="EURUSD-2014-01.csv"
    

def main():
    f = open(filename)
    x= []
    dt = []
    ybid = []
    yask = []
    cnt= 0
    marker_data = []
    cnt_data = []
    # init strategy variables
    armed = 4   # 4 wait for minimum diff to enable 
    maxima = 0
    rsi_val = 0.
    price_val = 0
    
    accdata = feedofcsv.AccData(1000)
    
    sma = feedofcsv.Ema(3*60)
    sma_data = []
    
    macd = feedofcsv.Macd(9*60,20*60,feedofcsv.Ema)
    macd_data = []
    
    macd_sma = []
       
    pfile = open("EURUSDq.pickle",'w')
    
    for l in f.readlines():
        cnt += 1
        ##skip until this tick 
        #if cnt < 30000:
        #    if not cnt%1000:
        #        print cnt
        #    continue
        ##stop after this tick 
        #if cnt >= 101000:
        #    break

        #name datetime bid ask
        s = l.split(",")
            
        datetime, millis = s[1].split('.')
        sec = calendar.timegm(time.strptime(datetime, "%Y%m%d %H:%M:%S"))
        secm = sec + int(millis) / 1000.
        
        bid, ask = float(s[2]), float(s[3])

        if not cnt%1000:
            print cnt, datetime
        
        cnt_data.append(cnt)
 
        x.append(secm)
        ybid.append(bid)
        yask.append(ask)
        
        if len(ybid)>= 2:
            tl = x[-2]
            t  = x[-1]
            dt.append(t-tl)
        else:
            dt.append(None)
               
        #bollinger_data.append(bollinger.update(dt[-1], bid))            
        #rsi_data.append(rsi.update(secm, bid))
        #rsi_avg_data.append(rsi_avg.update(dt[-1], rsi_data[-1]))
        
        macd_data.append(macd.update(secm,bid))
        
        sma_data.append(sma.update(secm,macd_data[-1][2]))
        
        macd_sma.append((macd_data[-1][2],sma_data[-1]))
         
        """
        strategy:
        check for peaks with bollinger 
        wait for extrema of price 
        check rsi to be significant and put or call
                
        """
        ########################################
        ### Strategy
        #######################################################
        # performance [184, 15, 191]
        # balance 13.6 current portfolio []
        # total actions 375.0
        # 
        # winratio 49.0666666667
        # 
        #######################################################
        
        #try:
        if len(x) >20:
            if armed  == 0 and abs(macd_data[-2][2]):
                if macd_data[-2][2] > sma_data[-2]: #was rising
                    if macd_data[-1][2] < sma_data[-1]: # is now falling  --> put
                        marker_data.append(((datetimemodule.datetime.fromtimestamp(secm)),(bid),'c*'))
                        armed = 1
                        
                if macd_data[-2][2] < sma_data[-2]: #was falling
                    if macd_data[-1][2] > sma_data[-1]: # is now rising --> call
                        marker_data.append(((datetimemodule.datetime.fromtimestamp(secm)),(bid),'c*'))
                        armed = 2
                        
            if armed == 1:
                if time.gmtime(x[-2]).tm_min < time.gmtime(x[-1]).tm_min:  # test on close if direction is as expected
                    n = len(x) -2
                    thisopen = None
                    while time.gmtime(x[n]).tm_min == time.gmtime(x[-2]).tm_min:
                        thisopen = ybid[n]  # this is the price of the current candle opening
                        n -= 1
                    if thisopen != None and bid < thisopen:
                        # put
                        armed = 3
                        expire = secm+60
                        print "sell " ,bid
                        marker_data.append((
                                             (
                                                 datetimemodule.datetime.fromtimestamp(secm),
                                                 datetimemodule.datetime.fromtimestamp(secm+60),
                                              ),
                                             (bid,bid),
                                             'v-'))
                        feedofcsv.Option(secm,bid,60,accdata, up=False)
                    else: 
                        armed = 4
                        
            if armed == 2:
                if time.gmtime(x[-2]).tm_min < time.gmtime(x[-1]).tm_min:  # test on close if direction is as expected
                    n = len(x)-2
                    thisopen = None
                    while time.gmtime(x[n]).tm_min == time.gmtime(x[-2]).tm_min:
                        thisopen = ybid[n]  # this is the price of the last candle opening  
                        n -= 1          
                    if thisopen != None and bid > thisopen:     
                        # call
                        armed = 3
                        expire = secm+60
                        print "buy " ,bid
                        marker_data.append((
                                            (
                                                 datetimemodule.datetime.fromtimestamp(secm),
                                                 datetimemodule.datetime.fromtimestamp(secm+60),
                                              ),
                                             (bid,bid),
                                             '^-'))
                        feedofcsv.Option(secm,bid,60,accdata, up=True)  
                    else: 
                        armed = 4
                        
            if armed == 3:
                if secm >= expire:
                    marker_data.append(((datetimemodule.datetime.fromtimestamp(secm)),(bid),'kx'))
                    armed = 4
            
            if armed == 4:
                diff = macd_data[-1][2] - sma_data[-1]
                if abs(diff) > 0.00008:
                    marker_data.append(((datetimemodule.datetime.fromtimestamp(secm)),(bid),'co'))
                    armed = 0
                      
        feedofcsv.Option.update(secm,accdata,bid)    
        #except Exception as e:
        #    print "we had a crash: ", e
        #    break
               
        ### end strategy
        ####################################
        
    wins = feedofcsv.Option.performance[0]
    losses = float(feedofcsv.Option.performance[2])
    clearedtotal = wins+losses
    
    print "#######################################################"
    print "# performance", feedofcsv.Option.performance
    print "# balance", accdata.balance, 
    print "current portfolio" , accdata.portfolio
    print "# total actions"  ,   clearedtotal
    if clearedtotal: #prevent div by zero
        print "# "
        print "# winratio", wins/clearedtotal * 100.
        print "# "
        print "#######################################################"        
  
    
    
    dates = [datetimemodule.datetime.fromtimestamp(ts) for ts in x]
    plt.subplots_adjust(bottom=0.2)
    plt.xticks( rotation=25 )
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    x = dates
    
    print "plot price"

    
    rows = 4   
    # price bollinger 
    ax1 = plt.subplot(rows, 1, 1)
    
    ax1.plot( x,ybid,'b-')  # sma_fast_data sma_slow_data
    ax1.grid(True)
    
    print "plot strategic markers"
    for line in marker_data:
        ax1.plot(*line,markersize=10)    
    
    ax2 = plt.subplot(rows, 1, 4, sharex=ax1)
    #par2 = ax2.twinx()
    ax2.plot(x, cnt_data ,'b.')
    ax2.grid(True)

    print "plot macd "
    #pipt, pipv = zip(*pippersec_t_v)
    ax3 = plt.subplot(rows, 1, 2, sharex=ax1)
    #par3 = ax3.twinx()
    ax3.plot(x, macd_sma ,'b-')
    #par3.plot(pipt, pipv, 'g-')
    ax3.grid(True)
    
    print "plot balance"
    ax4 = plt.subplot(rows, 1, 3, sharex=ax1)
    dths = [datetimemodule.datetime.fromtimestamp(ts) for ts in accdata.histstamps]
    dthds = [datetimemodule.datetime.fromtimestamp(ts) for ts in accdata.histdebtstamp]
    ax4.plot(dths, accdata.histbalance,'ko',dthds , accdata.histdebt,'ro')                                   # rsi
    ax4.grid(True)
    plt.show()
    
if __name__== "__main__":
    main()

