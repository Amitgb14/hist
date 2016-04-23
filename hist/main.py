import os
import sys
import time
import logging 
import subprocess
import argparse

HOST_CFG = 'host.cfg'
FILE_NAME = 'bash_history'
ctime = ''#time.strftime('%d-%y-%m %H:%M:%S')

class Hist:

  def __init__(self, args):
    self.arg         = args
    self.all         = False
    self.single_node = False
    self.verbose     = False
    self.print_hist  = False
    self.location    = ''
    self.history     = ''
    self._parse_args()

  def __del__(self):
    self.close_logging()

  def setup_logging(self):
    self.histlog = logging.getLogger("hist")
    self.histlog.setLevel(logging.INFO)
    print_console = logging.StreamHandler(sys.stdout)
    print_console.setFormatter(logging.Formatter('%(message)s'))
    print_console.setLevel(logging.INFO)
    self.histlog.addHandler(print_console)

  def close_logging(self):
    logging.shutdown()

  def check_node(self, node_ip):
    command = "ping {} -c 3 -W 5".format(node_ip)
    execute = subprocess.Popen(command, stdout=subprocess.PIPE, 
              stderr=subprocess.PIPE, shell=True)
    status = execute.wait()
    (stdout, stderr) = execute.communicate()
    if status:
      if status == 1:
        self.histlog.info(stdout.strip())
      else:
        self.histlog.info(stderr.strip())
      return False
    return True

  def save_history(self, node_ip, location=os.environ['HOME']+os.sep+'.'):
    if self.location:
      if self.location == '.':
        self.location = ''
      location = self.location
    history_file = location+node_ip+'@'+FILE_NAME+ctime
    try:
      with open(history_file, 'w') as fwrite:
        fwrite.write(self.history)
    except Exception as e:
      self.histlog.error(e)

  def show_history(self, node_ip, location=os.environ['HOME']+os.sep+'.'):
    if self.location:
      if self.location == '.':
        self.location = ''
      location = self.location
    history_file = location+node_ip+'@'+FILE_NAME+ctime
    if not os.path.exists(history_file):
      self.histlog.info("Not sync {} node".format(node_ip))
      return
    try:
      with open(history_file) as fread:
        for line in fread.readlines():
          self.histlog.info(line.strip())
    except Exception as e:
      self.histlog.error(e)

  def read_config(self):
    try:
      with open(HOST_CFG) as fread:
        datas = fread.readlines()
        ip_address = [ip.strip() for ip in datas if not ip.startswith("#")]
      return ip_address
    except Exception as e:
      self.histlog.error(e)
      return []

  def copy_node_key(self, node_ip):
    self.histlog.info("Try to connect new node {}".format(node_ip))
    if not self.check_node(node_ip):
      return False
    command = "ssh-copy-id "+node_ip
    execute = subprocess.Popen(command, stdout=subprocess.PIPE,
              stderr=subprocess.PIPE, shell=True)
    status = execute.wait()
    (stdout, stderr) = execute.communicate()
    if status:
      self.histlog.error("Error : {}".format(stdout))
      return False
    self.histlog.info("Successfully connected {}".format(node_ip))
    return True

  def add_node(self, node_ip):
    if os.path.exists(HOST_CFG):
      if node_ip in self.read_config():
        self.histlog.info("Node alrady in record")
        return
    if not self.copy_node_key(node_ip):
      return False
    try:
      with open(HOST_CFG, "a") as fwrite:
        fwrite.write(node_ip)  
    except Exception as e:
      self.histlog.error(e)

  def start_sync(self, node_ip):
    if not self.check_node(node_ip):
      self.histlog.warning("Node {} is not to connect".format(node_ip))
      return
    command = "ssh {0} cat ~/.{1}".format(node_ip, FILE_NAME)
    execute = subprocess.Popen(command, stdout=subprocess.PIPE, 
              stderr=subprocess.PIPE, shell=True)
    status = execute.wait()
    (stdout, stderr) = execute.communicate()
    if status:
      self.histlog.error("Error : {}".format(stderr))
      return False
    self.histlog.info("Successfully connected {}".format(node_ip))
    self.history = stdout

    if self.verbose:
      self.histlog.info(self.history)
    else:
      if self.print_hist:
        self.histlog.info(self.history)
      self.save_history(node_ip)

  def collect_sync(self, option=None):
    nodes = self.read_config()
    if option:
      if option in nodes:
        self.start_sync(option)   
    else:
      for node_ip in nodes:
       if node_ip:
         self.start_sync(node_ip)

  def list_nodes(self):
    if not os.path.exists(HOST_CFG):
      self.histlog.info("{} file not exists.".format(HOST_CFG))
      return
    try:
      with open(HOST_CFG) as fread:
        datas = fread.readlines()
        ip_address = [ip.strip() for ip in datas if not ip.startswith("#")]
      for ip in ip_address:
        self.histlog.info(ip)
    except Exception as e:
      self.histlog.error(e)

  def main(self, args):
    self.setup_logging()
    if args.list_nodes:
      self.list_nodes()
      return
    if args.sync_all:
      self.all = True
    if args.node_ip:
      self.single_node, node_ip = True, args.node_ip 
    if args.add_node:
      self.add_node(args.add_node)
      return
    if args.print_hist:
      self.print_hist, hist_node_ip = True, args.print_hist or False
    if args.verbose:
      self.verbose = True
    if args.location:
      self.location = args.location
    if self.all:
      print ("Start Sync All listed nodes")
      self.collect_sync()
    elif self.single_node:
      print ("Start Sync {} nodes".format(node_ip))
      self.collect_sync(node_ip)
    elif self.print_hist and hist_node_ip:
      self.show_history(hist_node_ip)

  def _parse_args(self):
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list-nodes", action="store_true",
                        dest="list_nodes", default=False,
                        help="Print all listed nodes.")
    parser.add_argument("-s", "--sync-all", action="store_true",
                        dest="sync_all", default=False,
                        help="Sync all listed nodes.")
    parser.add_argument("-n", "--node", action="store",
                        dest="node_ip", type=str,
                        help="Sync only by node IP address.")
    parser.add_argument("-a", "--add", action="store",
                        dest="add_node", type=str,
                        help="Add new node.")
    parser.add_argument("-p", "--print", action="store",
                        dest="print_hist", type=str, default='',
                        help="Print history.")
    parser.add_argument("-d", "--dir", action="store",
                        dest="location", type=str,
                        help="Save history file in given location.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        dest="verbose",
                        help="Print history without saving.")

    args = parser.parse_args()
    self.main(args)


if __name__ == '__main__':

  d = Hist(sys.argv[1:])
