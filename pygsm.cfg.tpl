[Logging]
; The full or relative path to the log file
; Permissions should be set properly for 
; this GSM instance to access
file        = pygsm.log
; The python log level.  
; See: https://docs.python.org/3/howto/logging.html#when-to-use-logging
level       = INFO

[Database]
; Hostname or IP address of DB server
hostname    = 127.0.0.1
; Port number of the DB server instance
port        = 5432
; The database name             
name        = pygsm
user        = 
password    = 

[Pref]
; Maximum age of games to display
; Default: 30
;game_max_age = 30           