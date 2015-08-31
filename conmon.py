#coding: utf-8
#!/usr/bin/python
import argparse , sys, time, os, re, subprocess
from threading import Thread

"""Conmon is network monitor which tracks the state of your Internet connection for given time and logs possible downtimes"""
   
class netmon(object):

    def __init__(self):
        self.color = '\033[92m'
        self.end_color = '\033[0m'
        
    def arguments(self):
        #Help text
        self.help = """Usage: netmon.py -t <Monitoring time> -i <Checking interval> [optional arguments]"""
        #Args
        self.parser = argparse.ArgumentParser(description=self.help)
        self.parser.add_argument("-t", "--time", type=str, help="Testing time - in minutes")
        self.parser.add_argument("-i", "--interval", type=str, help="Testing interval - in minutes")
        self.parser.add_argument("-d", "--dns", action='store_true', help="Keep track of dns status")
        self.args = self.parser.parse_args()
        self.dns = self.args.dns
        self.montime = self.args.time
        self.i_val = self.args.interval
        if not self.montime or not self.i_val:
            self.parser.print_help()
            sys.exit(0)
        if int(self.i_val) >  int(self.montime):
            print "[!] Monitoring time has to be longer than checking interval!"
            time.sleep(3)
            self.parser.print_help()
            sys.exit(0)
            
        if self.dns:
            self.dns = True
        return (self.montime, self.i_val, self.dns)

         
    def print_pos(self,y, x, text):
        sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
        sys.stdout.flush()
        
    def menu(self, *arg):
        if os.name == 'posix':
            os.system('clear')
        else:
            os.system('cls')
        self.print_pos(25, 5, self.color+"[!]Conmon is monitoring your Internet connection status"+self.end_color)
        if len(arg) > 0:
            self.t = int(arg[0])*60
            self.countdown(self.t)
        
        
    def countdown(self, time_):
        self.time_ = int(time_)
        while self.time_ > 0:
            self.print_pos(37,6,"Time left --> "+str(self.time_)+" seconds")
            time.sleep(1)
            self.time_ -= 1
            
        
    
    
    def log(self, caller):
        self.int_down = ' --> Internet connection down.'
        self.dns_down = ' --> DNS failed - Internet connection up.'
        self.up_again = ' --> Connection up again.'
        self.c = caller
        if self.c == 'ping_down':
           self.write_log(self.int_down)
            
        elif self.c == 'ping_up_dns_down':
            self.write_log(self.dns_down)
            
        elif self.c == 'up_again':
            self.write_log(self.up_again)
                   
    def write_log(self, data):
        self.clock = str("\n"+time.strftime("%X"))
        self.data = self.clock+data
        self.date_raw = str(time.strftime("%x"))
        self.log_name = "conmon_"+re.sub('[/]', '_', self.date_raw)+'.log'
        if os.path.isfile(self.log_name):
            self.l = open(self.log_name, 'a')
        else:
            self.l = open(self.log_name, 'w')
        self.l.write(self.data)
        self.l.close()
    
            
    def ping(self, targ):
        self.t = targ
        if os.name == 'posix':
            self.output = subprocess.check_output("ping -w 1 -c 1 "+self.t+" | grep icmp* | wc -l" , shell=True)
                  
        else:
            self.output_raw = subprocess.check_output("ping -n 1 " +self.t)
            if "Received = 1" in self.output_raw:
                self.output = "1"
            else:
                self.output = "0"
            
        return self.output
            
    def state(self, time_, interval, dns=False):
        self.time_ = time.time() + 60 * int(time_)
        self.i_val = int(interval)*60
        self.dns = dns
        self.up = True
        
            
        while time.time() < self.time_:
            if not self.dns:
                self.ping_ = self.ping('8.8.8.8')
                self.menu()
                if '0' in self.ping_:
                    if self.up:
                        self.log('ping_down')
                        self.up = False
                        
                else:
                    if not self.up:
                        self.log('up_again')
                        self.up = True

            
            if self.dns:
                self.ping_d = self.ping('google.com') #used if --dns selected
                self.ping_ = self.ping('8.8.8.8')
                if '0' in self.ping_d:
                    if '0' in self.ping_:
                        if self.up:
                            self.log('ping_down')
                            self.up = False
                            
                    elif '1' in self.ping_:
                        self.log('ping_up_dns_down')
                        self.up = False
                else:
                    if not self.up:
                        self.log('up_again')
                        self.up = True        
            time.sleep(self.i_val)
                              
    def main(self):
        self.t, self.i, self.d = self.arguments()
        #self.thread = Thread(target = self.state, args = (self.t, self.i, self.b, self.d ))
        #self.thread.start()
        #self.menu(self.t)
        self.state(self.t, self.i, self.d)
        #self.thread.join()
        
        
        
if __name__ == '__main__':
    netmon().main()
