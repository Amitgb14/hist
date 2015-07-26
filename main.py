import os
import subprocess
import sys
import time

HOST_CFG = 'host.cfg'
FILE_NAME = 'bash_history'
ctime = ''#time.strftime('%d-%y-%m %H:%M:%S')

class Hist:

  def __init__(self, args):
    self.arg = args
    self.sync = 0
    self.showOutput = 0
    self.machineid = []
    self.machines = {}
    self.chkArgs()

  def chkArgs(self):
    for arg in self.arg:
      if arg == '--sync':
        self.sync = 1
      elif arg[:3] == '--m':
	self.machineid.append(arg[3:])
    self.readConf()

  def readConf(self):
    machines = [line.strip().split() for line in open(HOST_CFG, "r").readlines() if not line.startswith('#')]
    for machine_id, machine in machines:
      self.machines[machine_id] =  machine

    if self.sync:
      for machine in self.machines:
        self.connect(self.machines[machine])
    elif self.machineid:
      for machine in self.machineid:
        if machine in self.machines:
          self.connect(self.machines[machine])
    else:
      print "Retrive from all machine"
      for machine in self.machines:
        self.connect(self.machines[machine])

  def connect(self, machine):
    print "try to connect "+machine
    cmd = "ssh %s cat ~/.%s"%(machine, FILE_NAME)
    history = ''
    execute = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    status = execute.wait()
    if status:
      print "Error : ",execute.communicate()[1]
      sys.exit(status)
    print "Successfully connected "+machine
    history = execute.communicate()[0]
    self.getHistory(machine, history)

  def getHistory(self, machine, history):
    filename = os.environ['HOME']+os.sep+'.'+machine+'@'+FILE_NAME+ctime
    writehis = open(filename, 'w')
    writehis.write(history)
    writehis.close()
    if self.showOutput:
      self.printHistory(filename)

  def printHistory(self, filename):
    with open(filename) as h:
      print h.read()

if __name__ == '__main__':
  
  if len(sys.argv) > 1:
    run = Hist(sys.argv[1:])
  else:
    print "python main.py [option]"
    print "--sync     Retrive from all machine"
    print "--m<id>    Retrive from single machine"
