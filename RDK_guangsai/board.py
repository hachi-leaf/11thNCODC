import Hobot.GPIO as GPIO
import time

HIGH = GPIO.HIGH
LOW = GPIO.LOW

GPIO.setmode(GPIO.BOARD)

GPIO.setup(37, GPIO.OUT)
GPIO.setup(36, GPIO.OUT)
GPIO.setup(29, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

GPIO.setup(22, GPIO.IN)
GPIO.setup(18, GPIO.IN)
GPIO.setup(13, GPIO.IN)
GPIO.setup(16, GPIO.IN)
GPIO.setup(11, GPIO.IN)
GPIO.setup(15, GPIO.IN)
        
class BOT():
    def __init__(self):
        self.time_blue = time.time()
        self.time_red = time.time()
        self.time_stop = time.time()
        self.time_reset = time.time()
        self.time_over = time.time()
        self.time_read = time.time()

    def open_board(self,mode):
        if mode != 0:
            GPIO.output(37, GPIO.HIGH)
        else:
            GPIO.output(37, GPIO.LOW)
            
    def open_red(self,mode):
        if mode != 0:
            GPIO.output(29, GPIO.HIGH)
        else:
            GPIO.output(29, GPIO.LOW)
            
    def open_blue(self,mode):
        if mode != 0:
            GPIO.output(26, GPIO.HIGH)
        else:
            GPIO.output(26, GPIO.LOW)
            
    def open_stop(self,mode):
        if mode != 0:
            GPIO.output(36, GPIO.HIGH)
        else:
            GPIO.output(36, GPIO.LOW)
            
    def bot_blue(self):
        return GPIO.input(22)
        
    def bot_red(self):
        return GPIO.input(18)
        
    def bot_stop(self):
        return GPIO.input(15)
        
    def bot_reset(self):
        return GPIO.input(16)
        
    def bot_over(self):
        return GPIO.input(11)
        
    def bot_read(self):
        return GPIO.input(13)
        
    def open_all(self,mode):
        if mode != 0:
            self.open_board(1)
            self.open_red(1)
            self.open_blue(1)
            self.open_stop(1)
        else:
            self.open_board(0)
            self.open_red(0)
            self.open_blue(0)
            self.open_stop(0)
    
    def flush(self):
        if self.bot_blue() == GPIO.HIGH:
            self.time_blue = time.time()
            
        if self.bot_red() == GPIO.HIGH:
            self.time_red = time.time()
            
        if self.bot_stop() == GPIO.HIGH:
            self.time_stop = time.time()
            
        if self.bot_reset() == GPIO.HIGH:
            self.time_blue = time.time()
            
        if self.bot_over() == GPIO.HIGH:
            self.time_over = time.time()
            
        if self.bot_read() == GPIO.HIGH:
            self.time_read = time.time()
            
            
            
        if time.time() - self.time_blue > 0.01:
            return 'blue'
            
        if time.time() - self.time_red > 0.01:
            return 'red'
            
        if time.time() - self.time_stop > 0.01:
            return 'stop'
            
        #if time.time() - self.time_reset > 1:
        #    return 'reset'
            
        if time.time() - self.time_over > 0.01:
            return 'over'
            
        if time.time() - self.time_read > 0.01:
            return 'read'
            
        return 0
    
        
if __name__=='__main__':
    bot = BOT()
    while True:
        print(bot.flush())