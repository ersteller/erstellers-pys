'''
Created on 05.04.2016

@author: jan


TODO check numpy array or dequeue for speed improvement
tODO make pandas dataframe from csv for cleanup and improved usability (less ifcases to handle none values)

TODO: later: MACD

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
    
    # init strategy variables
    armed = False
    maxima = 0
    rsi_val = 0.
    price_val = 0
    
    accdata = feedofcsv.AccData(1000)
    
    sma_fast = feedofcsv.Wmavrg(200)
    sma_fast_data = []
    sma_ff = feedofcsv.Wmavrg(6)
    sma_ff_data = []

    bollinger = feedofcsv.Bollinger(500,2)
    bollinger_data = []
    
    rsi = feedofcsv.RSI()
    rsi_data = []
    
    rsi_avg = feedofcsv.Wmavrg(3)
    rsi_avg_data = []
    
    pippersec = None
    pipperseclaststamp = 0
    pipperseclastprice = None
    pippersec_t_v = []
    
    try:
        pfile = open("EURUSD q.pickle",'r')
        
        (
                    x,
                    ybid,
                    yask,
                    sma_fast_data,
                    sma_ff_data,
                    bollinger_data,
                    marker_data,
                    rsi_data,
                    rsi_avg_data,
                    pippersec_t_v,
                    accdata
        ) = cPickle.load(pfile)
    except Exception as e:
        #raise e #forbid recalculation
        pfile = open("EURUSDq.pickle",'w')
        
        for l in f.readlines():
            cnt += 1
            ##skip until this tick 
            #if cnt < 100000:
            #    if not cnt%1000:
            #        print cnt
            #    continue
            ##stop after this tick 
            #if cnt >= 110000:
            #    break

            #name datetime bid ask
            s = l.split(",")
                
            datetime, millis = s[1].split('.')
            sec = calendar.timegm(time.strptime(datetime, "%Y%m%d %H:%M:%S"))
            secm = sec + int(millis) / 1000.
            
            bid, ask = float(s[2]), float(s[3])

            if not cnt%1000:
                print cnt, datetime
            
     
            x.append(secm)
            ybid.append(bid)
            yask.append(ask)
            
            if len(ybid)>= 2:
                tl = x[-2]
                t  = x[-1]
                dt.append(t-tl)
            else:
                dt.append(None)
            
            sma_fast_data.append(sma_fast.update(dt[-1], bid))
            sma_ff_data.append(sma_ff.update(dt[-1],bid))
            bollinger_data.append(bollinger.update(dt[-1], bid))            
            rsi_data.append(rsi.update(secm, bid))
            rsi_avg_data.append(rsi_avg.update(dt[-1], rsi_data[-1]))
            
            
            if pipperseclaststamp + 1 <= secm:
                if pipperseclastprice != None:                    
                    pricediff = bollinger_data[-1][0] - pipperseclastprice 
                    duration = (secm - pipperseclaststamp)
                    if duration != 0:
                        pippersec = pricediff/duration
                        pippersec_t_v.append((secm, pippersec))
                pipperseclaststamp = secm
                pipperseclastprice = bollinger_data[-1][0]
                
             
            """
            strategy:
            check for peaks with bollinger 
            wait for extrema of price 
            check rsi to be significant and put or call
                    
            """
            ########################################
            ### Strategy
            #######################################################
            # performance [218, 7, 129]
            # balance 1908.0 current portfolio []
            # total actions 347.0
            # 
            # winratio 62.8242074928
            # 
            #######################################################
            
            # begin test closing outside bollinger
            if len(x) > 2 and time.gmtime(x[-2]).tm_min < time.gmtime(x[-1]).tm_min:  # test only on new candle stick
                if not armed and (ybid[-2] > bollinger_data[-2][1] or ybid[-2] < bollinger_data[-2][2]):
                    armed = 1
                    esxtrema = sma_ff_data[-1]
                    marker_data.append(((datetimemodule.datetime.fromtimestamp(secm)),(bid),'c*'))
                    isup = True if ybid[-1] > bollinger_data[-1][0] else False  
                
            if armed == 1:
                # crawl on price until momentum turns,
                if isup:  # find max low 
                    if esxtrema <= sma_ff_data[-1]:
                        esxtrema = sma_ff_data[-1]
                    elif esxtrema > sma_ff_data[-1]:
                        # found peak maxima of price
                        if  rsi_avg_data[-1] > 0.74:
                            esxtrema = 0  # next stage
                            armed = 3
                            expire = secm+60
                            print "sell " ,bid , bollinger_data[1][-1], rsi_avg_data[-1]
                            marker_data.append((
                                                (
                                                    datetimemodule.datetime.fromtimestamp(secm),
                                                    datetimemodule.datetime.fromtimestamp(secm+60),
                                                 ),
                                                (bid,bid),
                                                'v-'))
                            feedofcsv.Option(secm,bid,60,accdata, up=False)
                        else:
                            #print "rsi not strong enough"
                            #marker_data.append(((secm),(bid),'kx'))
                            armed = 0
                            esxtrema = 0   
                if not isup:
                    if esxtrema >= sma_ff_data[-1]:
                        esxtrema = sma_ff_data[-1]
                    elif esxtrema < sma_ff_data[-1]:   #Todo: make a more sensable stop of interest 
                        # found peak maxima of price
                        if rsi_avg_data[-1] < 0.26:
                            esxtrema = 0  # next stage
                            armed = 3
                            expire = secm+60
                            print "buy " ,bid , bollinger_data[1][-1], rsi_avg_data[-1]
                            marker_data.append(((
                                                    datetimemodule.datetime.fromtimestamp(secm),
                                                    datetimemodule.datetime.fromtimestamp(secm+60),
                                                 ),
                                                (bid,bid),
                                                '^-'))
                            feedofcsv.Option(secm,bid,60,accdata, up=True)  
                        else:
                            #print "rsi not strong enough"
                            #marker_data.append(((secm),(bid),'kx'))
                            armed = 0
                            esxtrema = 0
            if armed == 3:
                if secm >= expire:
                    armed = 0
                    
            feedofcsv.Option.update(secm,accdata,bid)    
                    
            
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

        cPickle.dump(
                (
                    x,
                    ybid,
                    yask,
                    sma_fast_data,
                    sma_ff_data,
                    bollinger_data,
                    marker_data,
                    rsi_data,
                    rsi_avg_data,
                    pippersec_t_v,
                    accdata
                ), pfile)
    pfile.close()
    print "done saving cache now start plotting"
   
   
    bmean, bupper, blower = zip(*bollinger_data)
    
    
    
    dates = [datetimemodule.datetime.fromtimestamp(ts) for ts in x]
    plt.subplots_adjust(bottom=0.2)
    plt.xticks( rotation=25 )
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    x = dates
    
    print "plot price"

    
    rows = 3   
    # price bollinger 
    ax1 = plt.subplot(rows, 1, 1)
    
    ax1.plot( x,ybid,'b.', x,sma_ff_data, 'y.', x, sma_fast_data,'c.', x, bmean, 'r.')  # sma_fast_data sma_slow_data
    ax1.fill_between(x[1:], bupper[1:], blower[1:], color='b', alpha=0.2)
    ax1.grid(True)
    
    print "plot strategic markers"
    for line in marker_data:
        ax1.plot(*line,markersize=10)    
    #ax2 = plt.subplot(rows, 1, 2, sharex=ax1)
    #par2 = ax2.twinx()
    #ax2.grid(True)

    print "plot rsi"
    #pipt, pipv = zip(*pippersec_t_v)
    ax3 = plt.subplot(rows, 1, 2, sharex=ax1)
    #par3 = ax3.twinx()
    ax3.plot(x, rsi_data,'b.',x, rsi_avg_data, 'c.')
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

