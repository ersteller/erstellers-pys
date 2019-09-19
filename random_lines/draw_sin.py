'''
Created on 18.09.2013

@author: Jan
'''
from Tkinter import Tk, Canvas, Frame, BOTH
import threading
import random 
import sin16bit
import time

class Singraph(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent        
        self.initUI()
        
    def initUI(self):
        canvas = Canvas(self)
        self.canvas = canvas
        
        self.pack(fill=BOTH, expand=1)
        canvas.pack(fill=BOTH, expand=1)


    phase = 0
    rgb = 0,0,0
    
    def animate(self):
        
         
        Hex = '#%02x%02x%02x' % self.rgb
        
        self.phase0 = 0
        y0 = sin16bit.sinbitstepsphase(8,359, self.phase0)
        points0 = zip(range(360 + 1), y0)
        con0 = [(p1,p2) for p1,p2 in zip(points0[:-1],points0[1:])]
        
        self.phase1 = 2*sin16bit.pi/3.0
        y1 = sin16bit.sinbitstepsphase(8,360, self.phase1)
        points1 = zip(range(360 + 1), y1)
        con1 = [(p1,p2) for p1,p2 in zip(points1[:-1],points1[1:])]
        
        self.phase2 = 4*sin16bit.pi/3.0
        y2 = sin16bit.sinbitstepsphase(8,360, self.phase2)
        points2 = zip(range(360 + 1), y2)
        con2 = [(p1,p2) for p1,p2 in zip(points2[:-1],points2[1:])]
        
        for l0,l1,l2 in zip(con0, con1, con2):
            ((x01,y01),(x02,y02)) = l0
            ((x11,y11),(x12,y12)) = l1
            ((x21,y21),(x22,y22)) = l2
            self.canvas.create_line(x01,y01+1,x02,y02+1, fill=Hex)
            self.canvas.create_line(x11,y11+1,x12,y12+1, fill=Hex)
            self.canvas.create_line(x21,y21+1,x22,y22+1, fill=Hex)
            time.sleep(0.01)
        self.rgb = random.randint(0,255), random.randint(0,255), random.randint(0,255)
    
        

g = None

def sum_up(l):
    i = 0
    ret = []
    for e in l:
        i +=e
        ret.append(i)
    return ret
        
    

def main():
    loopthread = threading.Thread(target=mainthread, args=[])
    root = Tk()
    global g
    g = root
    
    root.geometry("720x260+100+100")    
    root.title("sinus")   
     
    loopthread.start() 
       
    root.mainloop()  
 
def mainthread():
    root = g
    #root.geometry("400x100+300+300")
    ex = Singraph(root)
    while 1:
        ex.animate()
    
    


if __name__ == '__main__':
    main() 