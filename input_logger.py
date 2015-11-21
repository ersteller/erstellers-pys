import sys
import pythoncom, pyHook 
import time

import threading


from Tkinter import Tk, Canvas, PhotoImage, mainloop


#global ginlogger

#def statikcallback(args):
	#ginlogger.OnEvent(args)


class InputLogger():
		
	#TODO: implement bedder synch because events start missing after some time
	lock = threading.Lock()
	
	f = open("log.txt",'w')
	
	window = Tk()
	
	hm = pyHook.HookManager()
		
	#TODO check for secondary display 
	
	def __init__(self):
		#global ginlogger
		#ginlogger = self
		# Get real screen dimension
		# TODO: check for secondary display or just expand with mouse range
		
		self.OnEvent = self.callbackOnEvent()
		
		screen_width = self.window.winfo_screenwidth()
		screen_height = self.window.winfo_screenheight() 
		self.WIDTH, self.HEIGHT = screen_width, screen_height
		
		self.minx = 0
		self.miny = 0
		self.maxx = self.WIDTH
		self.maxy = self.HEIGHT
		
		# make image for drawing
		self.canvas = Canvas(self.window, width=self.WIDTH, height=self.HEIGHT, bg="#000000")
		self.canvas.pack() 
		self.img = PhotoImage(width=self.WIDTH, height=self.HEIGHT)
		self.canvas.create_image((self.WIDTH/2, self.HEIGHT/2), image=self.img, state="normal")
		
		# save state 
		self.lastevent = []
		self.xl = []
		self.yl = []
		self.cl = []
		
		# setup hooks
		self.hm.KeyDown = self.OnEvent 
		self.hm.MouseAll = self.OnEvent
	
		self.hm.HookKeyboard() 
		self.hm.HookMouse()
	
	
	# this is the event callback for the windows pyhook
	def callbackOnEvent(self):
		self.n = 0
		def OnEvent(event):
			
			self.lastevent 
			t1 = int(round(time.time()*1000))
							
			#log only new entries to file
			currentevent = [i for i in event.__dict__.items() if "__" not in i[0]]  # convert class to list of attributes-names and values
			onlynew = [i for i in currentevent if i not in self.lastevent]               # only print changed attributes
			print t1, currentevent# onlynew  
			self.f.write(str(t1)+ str(currentevent)+"\n")  
			
			self.lastevent = currentevent
			
			# save position in instance
			if 'Position' in [k for k,v in currentevent]: 
				#self.lock.acquire()	
				self.xl.append(event.Position[0])
				self.yl.append(event.Position[1])
				self.cl.append(self.n)
				self.n+=1
				#print self.xl[-1] , self.yl[-1]		
				#self.lock.release()
			return True
		return OnEvent
	
		
	def loop(self):
		# TODO: split logging and display tasks !!!!!!!!
		updatetime = time.time()
		updatetimefile = time.time()
		while 1:
			pythoncom.PumpWaitingMessages()
			
			
			if len(self.xl):	
				#self.img.blank()
				self.img.put("#ff0000", (self.WIDTH/2, self.HEIGHT/2))
				
				commonlen = zip(self.xl,self.yl,self.cl)
				for x,y,c in commonlen:				
					self.img.put("#ffffff", (abs(x),abs(y)))
					
					# find extrema for x and y 
					if x < self.minx:
						self.minx = x
					elif x > self.maxx:
						self.maxx = x
					
					if y < self.miny:
						self.miny = y
					elif y > self.maxy:
						self.maxy = y
					
					#print c, x, y 
					# "del positions"
					
					#self.lock.acquire()
				del self.xl[:len(commonlen)]
				del self.yl[:len(commonlen)]
				del self.cl[:len(commonlen)]
					#self.lock.release()
					
			if time.time() > updatetime:	
				self.window.update()
				updatetime = time.time() + 1/60.
			#if time.time() > updatetimefile:
			#	print "flush"
				#self.f.flush()
				#self.canvas.postscript(file="pic.ps", colormode='color')
			#	updatetimefile = time.time() + 20
			
			#time.sleep(1)
				
if __name__ == "__main__":
	il = InputLogger()
	il.loop()