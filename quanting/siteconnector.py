'''
Created on 02.06.2016

@author: Jan
'''
try:
    from pywinauto import application, clipboard
except:
    print "you need pywinauto > v0.4  maybe update pywinauto"
    print "python -m pip install -U pywinauto"
    raise Exception('Module pywinauto required. \nYou need pywinauto > v0.4  maybe update pywinauto. \n    "python -m pip install -U pywinauto"')
import time

def buyoption(window, up=None, price=None, duration_pos=None):
    if price != None:
        window.BinaryOptionsTrading.ClickInput(coords=(960,240))
        window.BinaryOptionsTrading.TypeKeys('{HOME}{TAB}')
        window.BinaryOptionsTrading.ClickInput(coords=(960,240)) # enter price here 
        window.BinaryOptionsTrading.TypeKeys('^a'+str(int(price))+'{TAB}')
    if duration_pos != None:
        window.BinaryOptionsTrading.ClickInput(coords=(800,240))  # duration   
        window.BinaryOptionsTrading.TypeKeys('{HOME}'+'{DOWN}'*duration_pos+'{TAB}')     
             
    if up == True:
        window.BinaryOptionsTrading.ClickInput(coords=(960,380)) # up 
    elif up == False:
        window.BinaryOptionsTrading.ClickInput(coords=(960,480)) # down
    if up != None:
        time.sleep(2)
        window.BinaryOptionsTrading.ClickInput(coords=(960,310)) # return to trade
        time.sleep(3.5)
        window.BinaryOptionsTrading.ClickInput(coords=(460,360)) # 5 minuts view
    pass

def openBinaryoptionsDemoInChrome():
    app= application.Application()
    window = app.start_("I:\Program Files (x86)\Google\Chrome\Application\chrome.exe /new-window /window-position=10,10 /window-size=1200,1020 https://www.binaryoptionsdemo.com/en/trading/")
    time.sleep(6)
    print "rdy"
    return window

def getcurrtimepricebalancedemo(window):
    time.sleep(0.01)
    #window.SetFocus()
    clipboard.EmptyClipboard()
    window.BinaryOptionsTrading.TypeKeys('^a')
    time.sleep(0.01)
    window.BinaryOptionsTrading.TypeKeys('^c')
    time.sleep(0.05)
    sitetxt = clipboard.GetData()#.encode('ascii', 'ignore')
    # print sitetxt
    
    # search for time formated string
    preidx = sitetxt.find("Binary Options Demo")
    if preidx == -1:
        return None,None,None
    preidx += len("Binary Options Demo") 
    preidx += sitetxt[preidx:].find("\n") + len("\n") # idx now at beginning of tstr line 
    tstrlen = sitetxt[preidx:].find("\r\n")
    tstr = sitetxt[preidx:preidx+tstrlen]   
    ts = time.mktime(time.strptime(tstr, "%A, %B %d, %Y%H:%M:%S %Z "))

    # search for balance
    preidx = sitetxt.find("My Balance: $")
    if preidx == -1:
        return None,None,None  
    preidx += len("My Balance: $") 
    tstrlen = sitetxt[preidx:].find("\r\n")
    balancestr = sitetxt[preidx:preidx+tstrlen].replace(',', '')  # remove kilo delimiter
    balance = float(balancestr)
    
    # search for current price
    preidx = sitetxt.find("ALL") #    "\n\tEUR/USD " # for stockpair followed by current price
    if preidx == -1:
        return None,None,None
    pnline = sitetxt[preidx:].find("\n")
    enline = sitetxt[preidx+pnline+1:].find("\n")
    currpricestr = sitetxt[preidx+pnline+1:preidx+pnline+enline]
    currprice = float(currpricestr)
    return ts, currprice, balance

if __name__== "__main__":
    window = openBinaryoptionsDemoInChrome()
    ts0,price0,balance0 = getcurrtimepricebalancedemo(window)
        
    buyoption(window, price=5, duration_pos=1)
    
    breaktime = time.time() + 3
    while time.time() < breaktime:
        ts,price,balance = getcurrtimepricebalancedemo(window)
        print ts,price,balance
        #time.sleep(0.125)
    if ts0 == ts:
        raise Exception("could not extract increasing timestamp from site")
    else:
        print "Test passed"
