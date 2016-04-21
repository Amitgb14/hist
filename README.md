# Welcome to hist

hist is simple tool used to sync and get bash history from multiple node's.


How to run
-----------

```
    $ python main.py
```
```
    $ python main.py --sync [sync all machine]
```
```
    $ python main.py --m<inode-id>
```


Add new node
-------------

```
    $ ssh-copy-id <node> 
```

Write Host file
---------------

host.cfg

Manually write node with id 

```
  -----------------------------
  |  ID  | Node IP Address    |
  -----------------------------
  |  1   | 127.0.0.1          |
  -----------------------------
```

Add node by command-promot
```
    $ python main.py --add192.168.1.2
```
