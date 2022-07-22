# Readme
Squid authentication handler written in Python. Useful on systems where ncsa_auth is not available, or just systems where we would like better than MD5 or DES security. 

Single Python script, easy to install. The same script that's called by Squid can also be used to add users. BLAKE2 authentication is used and only salted hashes are stored. None the less it's probably a good idea to treat the hash file as secret. Just make sure that the Squid user has read permissions during operation, and that the user adding users has write permissions.  

The Python script can be called with parameters --user and --password to create new users. These users will be added to the hash database file that is specified in both normal operation as part of Squid, and in operation when adding users. 

Note that the database will not be reloaded live. meaning that if users are added you should restart Squid. Performance wise this is meant for relatively small user sets, though anything up to a few thousand users is probably fine performance wise. 

## Installation
Installation depends on your particular distribution. Example:

    cp auth.py /usr/local/bin/squid-auth.py 
    chmod +x /usr/local/bin/squid-auth.py
    /usr/local/bin/squid-auth.py /usr/local/etc/squid-user-db --user my_user --password my_password

Then add to your squid.conf, something like this:

    auth_param basic program /usr/bin/python /usr/local/bin/squid-auth.py /usr/local/etc/squid-user-db
    # how many instances of the above program should run concurrently
    auth_param basic children 5
    # display some message to clients when they are asked for username, password
    auth_param basic realm Please enter your proxy server username and password
    # for how much time the authentication should be valid
    auth_param basic credentialsttl 2 hours
    # whether username, password should be case sensitive or not
    auth_param basic casesensitive on

    # acl to force proxy authentication
    acl authenticated proxy_auth REQUIRED
    # acl to define IPs from your lan
    acl lan src 192.168.0.0/16
    # acl to force clients on your lan to authenticate
    http_access allow lan authenticated

Then restart Squid. 

## Examples
### Creating a new user
    $ python auth.py hash_db --user=testuser '--password=h$KJhafroq!M7fpaH'                                                                
    INFO:root:Creating user testuser in file hash_db
    INFO:root:Saving database
    INFO:root:Database saved
    $ cat .\hash_db                                                                                                                        
    testuser:cdc39abcb878e015de2412af737a2b35164db016830df80335cb388f016979e10ac04ee037b531e519fcd08cf535dae2844d9bd43d5ba27e3db6ccd583d24955


### Normal operation (usually started by Squid)
    testuser abcd
    WARNING:root:User testuser tried to authenticate: FAIL
    ERR
    testuser h$KJhafroq!M7fpaH
    INFO:root:User testuser tried to authenticate: Success
    OK
    testuser h$KJhafroq!M7fpaHx
    WARNING:root:User testuser tried to authenticate: FAIL
    ERR

Note that the logging output is sent to standard error, not standard output. 

### How do I view users/remove users/...
Just open the database file manually in a text editor and look/delete lines/... The format should be self-explanatory.