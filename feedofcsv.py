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
    
       
class Wmavrg(Mavrg):
    def __init__(self, timeframe):
        self.curtimeframe = 0
        Mavrg.__init__(self, timeframe)
        
    def update(self,dt,val):      
        """ dt should be the time interval for which val is hold
        """
        if val == None or math.isnan(val) or dt ==  0 or dt == None:
            #print "scip wavrg for ", val, dt
            return self.avrg #nothing changes
        
        self.samples.append((dt,val))
        self.samples_nonone.append(val)
        
        #update timeframe add sample
        if  self.avrg == None:
            self.avrg = 0
        self.avrg = (self.avrg * self.curtimeframe + val * dt ) / (self.curtimeframe + dt)
        self.curtimeframe += dt       
        
        # check limits of timeframe 
        while self.curtimeframe > self.maxsec and len(self.samples) > 2:
            pdt,pv = self.samples.popleft()
            del self.samples_nonone[0]
           
            # remove popped from timeframe and average
            self.avrg =  (self.avrg * self.curtimeframe - pv * pdt) / (self.curtimeframe - pdt)
            self.curtimeframe -= pdt 
        return self.avrg
    
    
class Bollinger(Wmavrg):
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

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class Option(Bunch):
    allopens={}
    performance=[0,0,0] #win pat loss
    
    def __init__(self, ts,curprice,duration,accdata,price=20, up=True,revenue=0.8):
            
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
                    result.append(opt.price * opt.revenue)
                    cls.performance[0] += 1
                
                elif curprice == opt.curprice:
                    # patt
                    accdata.changebalance(opt.price, t)
                    result.append(0)
                    cls.performance[1] += 1
                
                else:
                    #loss
                    result.append(-1*opt.price)
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
    