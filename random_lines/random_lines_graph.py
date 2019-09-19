from Tkinter import Tk, Canvas, Frame, BOTH
import threading
import random 

class RandomLinesGraph(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent        
        self.initUI()
        
    def initUI(self):
        canvas = Canvas(self)
        self.canvas = canvas
        
        self.pack(fill=BOTH, expand=1)
        canvas.pack(fill=BOTH, expand=1)
        #=======================================================================
        # s = sum_up([int(random.random()*2)*2-1 for _ in range(1000)])#int(  *2)*2-1
        # minimum = min(s)-1
        # s = [e - minimum for e in s]
        # points = zip(range(len(s)),s[:])
        # con = [(p1,p2) for p1,p2 in zip(points[:-1],points[1:])]
        # for l in con:
        #    ((x1,y1),(x2,y2)) = l
        #    canvas.create_line(x1,y1,x2,y2)
        # #print "done"
        #=======================================================================
        
    def animate(self):
        s = sum_up([(random.random()*2-1)*2 for _ in range(1000)])#int(  *2)*2-1
        minimum = -100#min(s)-1
        
        rgb = random.randint(0,255), random.randint(0,255), random.randint(0,255)
        Hex = '#%02x%02x%02x' % rgb
        
        s = [e - minimum for e in s]
        points = zip(range(len(s)),s[:])
        con = [(p1,p2) for p1,p2 in zip(points[:-1],points[1:])]
        for l in con:
            ((x1,y1),(x2,y2)) = l
            self.canvas.create_line(x1,y1,x2,y2, fill=Hex)
        #print "done"
        
        

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
    
    root.geometry("1000x200+100+100")    
    root.title("Colors")   
     
    loopthread.start() 
       
    root.mainloop()  
 
def mainthread():
    root = g
    #root.geometry("400x100+300+300")
    ex = RandomLinesGraph(root)
    while 1:
        ex.animate()
    
    


if __name__ == '__main__':
    main()