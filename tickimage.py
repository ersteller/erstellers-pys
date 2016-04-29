'''
Created on 05.04.2016

@author: jan
'''

import time 
import calendar

import numpy as np
import pandas
import matplotlib.pyplot as plt

import cPickle
import feedofcsv

filename="EURUSD-2014-01.csv"
    

def main():
    f = open(filename)
    x= []
    dt = []
    ybid = []
    yask = []
    ppsec = []
    frequ = []
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

    #sma_slow = feedofcsv.Mavrg(500)
    #sma_slow_data = []
    
    wsma_frequ_data = []
    wsma_frequ = feedofcsv.Wrate(3)
    
    rate = feedofcsv.Rate(3)
    rate_data = []
    #rate_fast = feedofcsv.Rate(0.3)
    #rate_data_fast = []

    rate_slow = feedofcsv.Rate(30)
    rate_slow_data = []
    
    sma_ppsec = feedofcsv.Mavrg(10)
    sma_ppsec_data = []
    
    bollinger = feedofcsv.Bollinger(500,2)
    bollinger_data = []
    
    rsi = feedofcsv.RSI()
    rsi_data = []
    
    rsi_avg = feedofcsv.Wmavrg(3)
    rsi_avg_data = []
    
    try:
        pfile = open("EURUSD 5.pickle",'r')
        
        (
                    x,
                    ybid,
                    yask,
                    ppsec,
                    frequ,
                    wsma_frequ_data,
                    rate_data,
                    rate_slow_data,
                    sma_fast_data,
                    sma_ppsec_data,
                    bollinger_data,
                    marker_data,
                    rsi_data,
                    rsi_avg_data,
                    accdata
        ) = cPickle.load(pfile)
    except Exception as e:
        #raise e #forbid recalculation
        pfile = open("EURUSD5.pickle",'w')
        
        for l in f.readlines():
            #name datetime bid ask
            s = l.split(",")
                
            datetime, millis = s[1].split('.')
            sec = calendar.timegm(time.strptime(datetime, "%Y%m%d %H:%M:%S"))
            secm = sec + int(millis) / 1000.
            
            bid, ask = float(s[2]), float(s[3])
            cnt += 1
            if not cnt%1000:
                print cnt, datetime
            
            #skip until this tick 
            if cnt < 160000:
                continue
            #stop after this tick 
            if cnt >= 200000:
                break
     
            x.append(secm)
            ybid.append(bid)
            yask.append(ask)
            
            # do the averaging
            #sma_slow_data.append(sma_slow.update(secm, bid))
            # dx = np.append([None],np.diff(x,1))
            # dy = np.append([None],np.diff(ybid,1))
            # ppsec = dy/dx
            # frequ = 1/dx
            
            if len(ybid)>= 2:
                tl = x[-2]
                t  = x[-1]
                yl = ybid[-2]
                y  = ybid[-1]
                
                dt.append(t-tl)
                if (t != tl):
                    # todo average those
                    # differenciate 
                    ppsec.append((y-yl)/(t-tl))
                    # tick frequency 
                    frequ.append(1/(t-tl))
                else:
                    ppsec.append(None)
                    frequ.append(None)
            else:
                ppsec.append(None)
                frequ.append(None)
                dt.append(None)
            
            sma_fast_data.append(sma_fast.update(dt[-1], bid))
            bollinger_data.append(bollinger.update(dt[-1], bid))
                
            #sma_frequ_data.append(sma_frequ.update(secm, 1))
            #rate_data_fast.append(rate_fast.update(secm))
            
            wsma_frequ_data.append(wsma_frequ.update(secm)) 
            rate_data.append(rate.update(secm))
            rate_slow_data.append(rate_slow.update(secm))
            sma_ppsec_data.append(sma_ppsec.update(secm,ppsec[-1]))
            
            rsi_data.append(rsi.update(secm, bid))
               
            rsi_avg_data.append(rsi_avg.update(dt[-1], rsi_data[-1]))
               
            
            ########################################
            ### Strategy
                        
            try:
                rate_low = min(rate_slow_data[-100:-1])
            except:
                rate_low = 0.1
            
            # begin on rising frequency of ticks
            if not armed and rate_slow_data[-1] > 3.9 and rate_slow_data[-1] > rate_low*2 and rate_slow_data[-2] <= rate_low*2:
                armed = 1
                maxima = rate_slow_data[-1]
                marker_data.append(((secm),(bid),'c*'))
                
            if armed == 1:
                # crawl on rising until it peaks, 
                if maxima <= rate_slow_data[-1]:
                    maxima = rate_slow_data[-1]
                elif maxima > rate_slow_data[-1]+0.3:
                    # found peak maxima of tickrate
                    marker_data.append(((secm),(bid),'c1'))
                    armed = 2
                    maxima = 0  # next stage
                    rsi_val = abs(rsi_avg_data[-1] - 0.5)
                    
                #elif rate_slow_data[-1] < 3.9:
                #    #print "ignore"  
                #    armed = False
                #    maxima = 0 
                    #===========================================================
                    # if rsi_data[-1] > 0.6:
                    #     print "sell rsi"
                    # elif rsi_data[-1] < 0.4:
                    #     print "buy rsi"     
                    # else:
                    #===========================================================
                    
                    # TODO: begin on rising frequency of ticks , 
                    #       crawl on rising until it peaks, 
                    #           find peak in rsi if peak is in extrema make trade   
                        
            
            if armed == 2:
                # wait for rsi to become even stronger
                if abs(rsi_avg_data[-1] - 0.5) < 0.2: # rsi not in interesting range
                    armed = 0# reset our statemachine because we lost interest in this point
                    print "too boring ",bid , bollinger_data[1][-1], rsi_avg_data[-1]
                    marker_data.append(((secm),(bid),'cx'))
                elif rsi_val <= abs(rsi_avg_data[-1] - 0.5):
                    rsi_val = abs(rsi_avg_data[-1] - 0.5)
                else: 
                    # found less strong rsi avrg val this means counter impuls is beginning
                    armed = 3
                    price_val = sma_fast_data[-1]
                    marker_data.append(((secm),(bid),'c2'))
                    
            if armed == 3:
                # TODO: maybe wait for price to reverse momentum and muve in direction predicted by rsi
                # eg rsi = 0.2 price should rise soon but it likey falls because of tickpeak width 
                #    still inducing momentum in same direction  
                try:  
                    # maybe we have no sufficient funds  
                    #    but we still want to be able to draw some graph of this fail
                    if rsi_avg_data[-1] > 0.5:
                        # we wait while price is still rising with the momentum (for falling fast avg)
                        if price_val <= sma_fast_data[-1]:
                            price_val = sma_fast_data[-1]  # it is still rising 
                        elif price_val > sma_fast_data[-1]:
                            print "sell",bid , bollinger_data[1][-1], rsi_avg_data[-1]
                            marker_data.append(((secm,secm+60,),(bid,bid),'v-'))
                            feedofcsv.Option(secm,bid,60,accdata, up=False)
                            armed = 0
                        
                    elif rsi_avg_data[-1] < 0.5: # wait for end of down momentum of price
                        if price_val >= sma_fast_data[-1]:
                            price_val = sma_fast_data[-1]  # it is still falling 
                        elif price_val < sma_fast_data[-1]:
                            print "buy " ,bid , bollinger_data[1][-1], rsi_avg_data[-1]
                            marker_data.append(((secm,secm+60,),(bid,bid),'^-'))
                            feedofcsv.Option(secm,bid,60,accdata, up=True)  
                            armed = 0
                except Exception as e:
                    print e.message
                    break
              
                 
                #===============================================================
                # #    but we still want to be able to draw some graph of this fail
                # if bid > bollinger_data[1][-1] or bid < bollinger_data[2][-1]:
                #     # we have now an out of bollinger price 
                #     if rsi_avg_data[-1] > 0.75:
                #         print "sell",bid , bollinger_data[1][-1], rsi_avg_data[-1]
                #         marker_data.append(((secm,secm+60,),(bid,bid),'v-'))
                #         
                #     elif rsi_avg_data[-1] < 0.25:                             
                #         print "buy " ,bid , bollinger_data[1][-1], rsi_avg_data[-1]
                #         marker_data.append(((secm,secm+60,),(bid,bid),'^-'))
                #                                  
                #===============================================================
            
                
                    
            feedofcsv.Option.update(secm,accdata,bid)    
                    
            
            
            
            ### end strategy
            ####################################
        print "#######################################################"
        print "performance", feedofcsv.Option.performance
        print "balance", accdata.balance, 
        print "current portfolio" , accdata.portfolio
        
        wins = feedofcsv.Option.performance[0]
        losses = float(feedofcsv.Option.performance[2])
        clearedtotal = wins+losses
   
        print "total actions"  ,   clearedtotal
        if clearedtotal: #revent div by zero
            print ""
            print "winratio", wins/clearedtotal * 100.
            print ""
            print "#######################################################"        

        cPickle.dump(
                (
                    x,
                    ybid,
                    yask,
                    ppsec,
                    frequ,
                    wsma_frequ_data,
                    rate_data,
                    rate_slow_data,
                    sma_fast_data,
                    sma_ppsec_data,
                    bollinger_data,
                    marker_data,
                    rsi_data,
                    rsi_avg_data,
                    accdata
                ), pfile)
    pfile.close()
    
    """
    strategy:
    add faster frequ average 
    check for threshold on freq long averaged
    wait for low of freq fast average
    use rsi for put or call  
    

    TODO: include option from feedofcsv
    cleanup option with accdatat class 
    TODO check numpy array or dequeue for speed improvement
    tODO make pandas dataframe from csv for cleanup and improved usability (less ifcases to handle none values)
    
    
    TODO: later: MACD
   """
   
    bmean, bupper, blower = zip(*bollinger_data)
    
    print marker_data
    
    
    
    
    rows = 4   
    # price bollinger 
    ax1 = plt.subplot(rows, 1, 1)
    
    ax1.plot(x, sma_fast_data,'c.', x,ybid,'b.', x, bmean, 'r.')  # sma_fast_data sma_slow_data
    ax1.fill_between(x[1:], bupper[1:], blower[1:], color='b', alpha=0.2)
    ax1.grid(True)
    for line in marker_data:
        ax1.plot(*line,markersize=10)    
    
    # Tick frequency
    ax2 = plt.subplot(rows, 1, 2, sharex=ax1)
    par2 = ax2.twinx()
    ax2.plot(x,frequ,'b.',)                  # tick frequency
    par2.plot( x,rate_data,'c.', x, rate_slow_data,'r.',x, wsma_frequ_data, 'g.' )
    ax2.grid(True)

    ax3 = plt.subplot(rows, 1, 3, sharex=ax1)
    par3 = ax3.twinx()
    ax3.plot(x,sma_ppsec_data,'g.')                  # driftspeed
    par3.plot(x, rsi_data,'b.',x, rsi_avg_data, 'c.')
    ax3.grid(True)
    
    ax4 = plt.subplot(rows, 1, 4, sharex=ax1)
    ax4.plot(accdata.histstamps, accdata.histbalance,'ko',accdata.histdebtstamp, accdata.histdebt,'ro')                                   # rsi
    ax4.grid(True)
    
    

    plt.show()
    
if __name__== "__main__":
    main()

