# Welcome to hist

hist is simple tool used to sync and get bash history from remote node's.
Save bash history in default home direcotry in 
```.<ip_address>@bash_history``` file format. 

How to run
-----------

```
    $ python run.py
```

Sync all nodes
```
    $ python run.py -s
```

Sync from 127.0.0.1 node
```
    $ python run.py -m 127.0.0.1
```

Save sync file in user defined location
```
    $ python run.py -m 127.0.0.1 -d .
```


Copy ssh key
-------------

```
    $ ssh-copy-id <node_ip_address> 
```

Write Host file
---------------

host.cfg

Manually add node 

```
  -----------------
  | IP Address    |
  -----------------
  | 127.0.0.1     |
  -----------------
```

Add node by command-promot
```
    $ python main.py -a 192.168.1.2
```

