#!/usr/bin/python
 
""" 
Authentication module for usage with Squid (proxy). Can be used to add new users as well. 
"""
import hashlib
import os
import re
import sys
import argparse
import logging


def matchpasswd(users, username, passwd):
    """USAGE:The function returns True if the user and passwd match False otherwise"""
    entry = (username, hash(username, passwd))
    return entry in users

def hash(username, passwd):
    h = hashlib.blake2b(salt=f"squid-{username}".encode("utf-8"))
    h.update(passwd.encode("utf-8"))
    return h.hexdigest()

def save_database(hash_file, users):
    logging.info("Saving database")
    with open(hash_file, "w") as f:
        f.write("\n".join([ f"{username}:{pw_hash}" for (username, pw_hash) in users]))
    logging.info("Database saved")

def load_database(hash_file):
    logging.debug("Reading hash database")
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Parse lines
    users = [ tuple(line.strip().split(":")) for line in lines]

    irregular_users = [ user for user in users if len(user) != 2]
    if len(irregular_users) > 0:
        logging.fatal("{hash_file} is corrupted, cannot proceed.")
        exit(1)
    return users

def update_user(hash_file, username, password):
    logging.info(f"Creating user {username} in file {hash_file}")

    users = load_database(hash_file)

    # if user already existed, filter him out
    users = [ (user, hash) for (user, hash) in users if user != username ]
    users.append((username, hash(username, password)))

    save_database(hash_file, users)

logging.basicConfig(encoding='utf-8', level=logging.INFO)

try:
    parser = argparse.ArgumentParser(description='Squid authentication mode.')
    parser.add_argument('hash_db', type=str,
                        help='Path to the file containing authentication hashes. Will be created if needed.')

    parser.add_argument('--user', 
                        help='Username for the user that will be created or updated')
    parser.add_argument('--password', 
                        help='Password for the user that will be created or updated')

    args = parser.parse_args()


    if args.user != None and args.password != None:

        if re.search("[^a-zA-Z0-9._]", args.user) != None:
            logging.error("Username cannot contain non-alphanumeric characters other than . and _.")
            exit(2)

        update_user(args.hash_db, args.user, args.password)
    else:
        logging.info(f"Using password file {args.hash_db}, waiting for username and password. " \
            "Enter username<space>password<ENTER> and receive OK if authentication is succesful or ERR if unsuccesful.")
        users = load_database(args.hash_db)

        while True:
            # read a line from stdin
            line = sys.stdin.readline()
            # remove '\n' from line
            line = line.strip()
            # extract username and password from line
            username = line[:line.find(' ')]
            password = line[line.find(' ')+1:]
        
            if matchpasswd(users, username, password):
                logging.info(f"User {username} tried to authenticate: Success")
                sys.stdout.write('OK\n')
            else:
                logging.warning(f"User {username} tried to authenticate: FAIL")
                sys.stdout.write('ERR\n')

            sys.stdout.flush()
except Exception as e:
    logging.error(e)