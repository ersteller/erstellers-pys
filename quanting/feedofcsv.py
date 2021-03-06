'''
Created on 18.03.2015

@author: Jan
'''

import time 
import calendar
import pylab
from matplotlib.backends import pylab_setup
import math

from collections import deque
import numpy as np

"""
avrg = (X*Wx+Y*Wy)/(Wx+Wy)

X = (Avrg*(Wx+Wy)-Y*Wy)/Wx

"""


def datafeed(datahandler, filename="EURUSD-2014-01.csv",param=None):
    
    f = open(filename)
       
    for l in f.readlines():
        #name datetime bid ask
        s = l.split(",")
        
        datetime, millis = s[1].split('.')
        sec = calendar.timegm(time.strptime(datetime, "%Y%m%d %H:%M:%S"))
        secm = sec + int(millis) / 1000.
        
        bid, ask = float(s[2]), float(s[3])
        
        datahandler(secm,bid,ask,param)
        
    f.close()
    
    
    
class RSI():
    def __init__(self, n=14*6):
        self.n = n # in sec
        self.deltas = deque()
        self.stamps = deque()
        self.up = 0
        self.down = 0
        self.prev = None
        
    def update(self, t, price):
        
        # TODO: make it more accurate like the realdeal with periodisation  
        self.stamps.append(t)
        if self.prev == None:
            self.prev = price
            self.deltas.append(0)
            return None
        
        # we have a prev now
        self.deltas.append(price - self.prev)
        self.prev = price
        
        while len(self.stamps) > self.n :
            pstamp = self.stamps.popleft()
            pdelta = self.deltas.popleft()
        
        deltas = np.array(self.deltas)
        
        totaltime = self.stamps[-1]-self.stamps[0]        
        avgu = deltas[deltas >= 0].sum()/totaltime
        avgd = deltas[deltas < 0].sum()/totaltime
        
        rsi = avgu/(avgu-avgd)
        return rsi      
        
    
class Mavrg():
    def __init__(self, timeframe):
        self.maxsec = timeframe
        self.avrg = None
        self.samples = deque()
        self.samples_nonone = deque()
                
    def update(self, t, val):
        
        if val == None:
            #print "scip wavrg for ", val, dt
            return self.avrg #nothing changes
        
        self.samples.append((t,val))
        self.samples_nonone.append(val)
        
        #update timeframe
        while t - self.samples[0][0] > self.maxsec:
            del self.samples[0]
            del self.samples_nonone[0]
            
        self.avrg = sum(self.samples_nonone) / len(self.samples) 
        #TODO: self.weighted_avrg
        return self.avrg 
    
class Rate(Mavrg):
    """ average of samples in last timeframe / sec """
    def __init__(self, timeframe):
        Mavrg.__init__(self, timeframe)
    def update(self,t):
        self.samples.append(t)
        while t - self.samples[0] > self.maxsec:
            del self.samples[0]
        return  float(len(self.samples)) / self.maxsec
    
class Wrate(Rate):
    """ averaged intervaltime weighted by intervaltime """
    def __init__(self, timeframe):
        Rate.__init__(self, timeframe)
        self.avrg = 0
        self.curtimeframe = 0
        
    def update(self,t):
        self.samples.append(t)
        
        if len(self.samples) < 2: 
            return self.avrg
                    
        dt = self.samples[-1] - self.samples[-2]   
        
        if self.curtimeframe == 0 and dt == 0:
            return self.avrg
        
        self.avrg = (self.avrg * self.curtimeframe + dt * dt) / (self.curtimeframe + dt)
        self.curtimeframe += dt
        
        # TODO: fix negative period time         
        while t - self.samples[0] > self.maxsec:
            pt = self.samples.popleft()
            del self.samples[0]
            if  len(self.samples) != 0:
                pdt = self.samples[0] - pt
            
                #remove popped timestamp from average  
                if self.curtimeframe-pdt <= 0:
                    self.curtimeframe = 0
                    self.avrgdt = 0
                    return 0
                self.avrg = (self.avrg * self.curtimeframe - pdt * pdt) / (self.curtimeframe - pdt)
                self.curtimeframe -= pdt
            else: 
                self.avrg = 0
                self.curtimeframe = 0
                break
                
        return self.avrg
    
class Ema():
    def __init__(self, timeframe):
        self.timeframe=timeframe
        self.alpha = 1./timeframe *2
        self.avg = None
        self.lasttime = None
        self.lastvalue = None
        
    def update(self, t, value):
        if self.avg == None: # first 
            self.avg = value
            self.lastvalue = value
            self.lasttime = t
            return self.avg
        dt = t - self.lasttime  # we calculate dt as the time to the next sample
        self.avg = self.alpha*dt * self.lastvalue + (1-self.alpha*dt)*self.avg
        self.lasttime = t
        self.lastvalue = value
        return self.avg
       
class Wmavrg(Mavrg):
    def __init__(self, timeframe):
        self.curtimeframe = 0
        self.lasttime = None
        self.lastvalue = None
        Mavrg.__init__(self, timeframe)
        
    def update(self,t,val):      
        if t == None or val == None or math.isnan(val):
            return None
        
        if self.lasttime == None:
            self.lasttime = t
            self.lastvalue = val
            self.avrg = val
            return None # only update last values on first update
        
        # ignore useless samples         
        dt = t - self.lasttime
        if val == None or math.isnan(val):
            #print "scip wavrg for ", val, dt
            return self.avrg #nothing changes
        if t == self.lasttime:
            self.lastvalue = val # overwrite value of noneduration samples 
            return self.avrg 
        
        self.samples.append((dt,self.lastvalue))
        self.samples_nonone.append(self.lastvalue)
        
        #update timeframe add sample
        self.avrg = (self.avrg * self.curtimeframe + self.lastvalue * dt ) / (self.curtimeframe + dt)
        self.curtimeframe += dt       
        
        # check limits of timeframe 
        while self.curtimeframe > self.maxsec and len(self.samples) > 2:
            pdt,pv = self.samples.popleft()
            del self.samples_nonone[0]
           
            # remove popped from timeframe and average
            self.avrg =  (self.avrg * self.curtimeframe - pv * pdt) / (self.curtimeframe - pdt)
            self.curtimeframe -= pdt 
        
        self.lasttime = t
        self.lastvalue = val 
        return self.avrg
    
    
class Bollinger(Ema):
    def __init__(self, timeframe=24*3600*20, k=2):
        Ema.__init__(self,timeframe)
        self.variance = 0
        self.stddev = math.sqrt(self.variance)
        self.k = k
        self.__samples = []#
        self.__samples_nonone = []
        
    def update(self,t,val):
        oldavg = self.avg
        avrg = Ema.update(self,t,val)
        
        self.__samples.append((t,self.lastvalue))
        self.__samples_nonone.append(self.lastvalue)
        
        if oldavg == None:
            self.first_t = t 
            return (None,None,None)
        newavg = avrg
        
        # check limits of timeframe 
        while t - self.__samples[0][0] > self.timeframe and len(self.__samples) > 2:
            _, pv = self.__samples.pop(0)
            del self.__samples_nonone[0]
            #self.variance += (val-pv)*(val-newavg+pv-oldavg)/(self.timeframe) # this seems to use constant number of samples
            #std = math.sqrt(self.variance)
            
        std = pylab.std(self.__samples_nonone)*self.k # this takes long
        
        if avrg != None:
            return avrg,avrg+std,avrg-std
        else:
            return (None,None,None)
        
class BollingerW(Wmavrg):
    def __init__(self, timeframe=24*3600*20, k=2):
        Wmavrg.__init__(self,timeframe)
        self.k = k
        
    def update(self,dt,val):
        avrg = Wmavrg.update(self,dt,val)
        std = pylab.std(self.samples_nonone)*self.k # this takes long
        if avrg != None:
            return avrg,avrg+std,avrg-std
        else:
            return (None,None,None)
        
class Macd():
    def __init__(self, _short=200,_long=500, avgtype=Ema):
        self._short = avgtype(_short)
        self._long = avgtype(_long)
        
    def update(self,t,val):
        sa = self._short.update(t,val)
        la = self._long.update(t,val)
        if sa == None or la == None:
            return None,None,None
        return sa, la, sa - la

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class Option(Bunch):
    allopens={}
    performance=[0,0,0] #win pat loss
    
    def __init__(self, ts,curprice,duration,accdata,price=20, up=True,revenue=0.77):
            
        Bunch.__init__(self, ts=ts,curprice=curprice,duration=duration,price=price,up=up,revenue=revenue)
        #check funds
        accdata.changebalance(-price,ts)
        accdata.portfolio.append(self)
        print self.__dict__ , self.performance
        #put self in the reference list
        self.allopens.update({self:None})
                
        
    @classmethod
    def update(cls, t,accdata,curprice):
        result = []
        for opt in accdata.portfolio[:]:
            if t > opt.ts + opt.duration:
                #expired
                
                #get if we are in the money
                if any([
                        curprice > opt.curprice and opt.up,  
                        curprice < opt.curprice and not opt.up
                        ]
                       ):
                    # win
                    accdata.changebalance( opt.price + opt.price * opt.revenue, t)
                    accdata.histtrade.append((t, opt.price * opt.revenue, opt.up))
                    result.append(opt.price * opt.revenue)
                    cls.performance[0] += 1
                
                elif curprice == opt.curprice:
                    # patt
                    accdata.changebalance(opt.price, t)
                    accdata.histtrade.append((t, 0, opt.up))
                    result.append(0)
                    cls.performance[1] += 1
                
                else:
                    #loss
                    result.append(-1*opt.price)
                    accdata.histtrade.append((t, -opt.price, opt.up))
                    cls.performance[2] += 1
                    pass
                    
                # remove expired option
                try:
                    del cls.allopens[opt]
                except:
                    raise Exception( "failed to delete expired option in our internal reference list")
                    
                del accdata.portfolio[accdata.portfolio.index(opt)]
                
            else:
                continue 
        return result


class AccData():
    def __init__(self,balance):
        self.portfolio = []
        self.balance = balance
        self.histstamps = []
        self.histbalance = []
        self.histdebt = []
        self.histdebtstamp = []
        self.histtrade = []
        
    def changebalance(self, diff, t=None):
        if self.balance < - diff:
            raise Exception("crash")          
        else:
            self.balance +=diff
            if t != None:
                self.histstamps.append(t)
                self.histbalance.append(self.balance)
                if diff < 0:
                    self.histdebt.append(self.balance)
                    self.histdebtstamp.append(t)     
            print "balance ", self.balance
            
def test():
    import matplotlib.pyplot as plt
    
    avrg = Mavrg(200)

    def handler(t,b,a,args):
        avrg = args[1]
        a = avrg.update(t, b)
        print t,b,a
        plt.plot(t,b,'bo',t,a,'r.')
        #plt.autoscale()
        if time.time() - args[0] > 5:
            plt.draw()
            plt.pause(0.01)
            args[0] = time.time() 
            
    # plot tuples from file
    args = [time.time(),avrg]
    plt.draw()
    plt.pause(0.1)
    plt.plot(hold=True)
    
    datafeed(handler,param=args)
     
if __name__ == "__main__":
    test()
    
