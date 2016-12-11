# Python Game Server Manager (pygsm)

To store and provide information about running game servers

## Setup

### Install Dependencies 

`pip install -r requirements.txt`

### Configure

Copy `pygsm.cfg.tpl` to `pygsm.cfg`.  

```
cp pygsm.cfg.tpl pygsm.cfg
```

Then edit `pygsm.cfg` with the proper configuration for your instance.  The `Database` and `Logging` sections are required.

## Run

You can run it simply by using the command `hug -f pygsm.py`.  This is not exactly appropriate for production use, so see the following section for setup with WSGI.

### WSGI 

TODO