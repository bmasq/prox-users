#!/usr/bin/python3

import json
import subprocess
import sys
from unidecode import unidecode

# Creates default:
# username <first letter of first name><first surname> lowercase
# password <first surname><first name>
def createUserPass(fname, surnames):
    #removes accents and other non-ASCII things
    fname = unidecode(fname)
    surnames = unidecode(surnames)
    fname = fname.split()
    surnames = surnames.split()
    user = fname[0][0].lower() + surnames[0].lower() + "@pve"
    pasw = surnames[0] + fname[0]
    return user, pasw

# main

batch = dict()
try:
    filename = sys.argv[1]
    with open(filename, "r") as f:
        batch = json.load(f)
    for user in batch.values():
        if ("firstname" not in user or "lastname" not in user
            or user["firstname"] == "" or user["lastname"] == ""):
            raise ValueError
except IndexError:
    print("usage: {} <json file>".format(sys.argv[0].split('/')[-1]))
except ValueError:
    print("ERROR: One or more users do not have a first- or lastname. Please check.")
except FileNotFoundError:
    print("ERROR: The specified file was not found")
except PermissionError:
    print("ERROR: You do not have permission to access the file")
except json.decoder.JSONDecodeError:
    print("ERROR: The file does not contain valid JSON data")
except UnicodeDecodeError:
    print("ERROR: The file contains non-UTF-8 characters")
except:
    print("Some unknown error occurred...")



for user in batch.values():
    # sets username and def. one-use-password
    userPass = createUserPass(user["firstname"], user["lastname"])
    username = userPass[0]
    password = userPass[1]
    # command minimum parameters
    command = [
    "pveum", "useradd", username, "--password", password,
    "--firstname", user["firstname"],
    "--lastname", user["lastname"]
    ]
    # sets optional parameters
    if "email" in user and user["email"] != "":
        command.append("--email")
        command.append(user["email"])
    if ("groups" not in user or  user["groups"] == ""):
        print("WARNING: user {} {} has no group(s) assigned"
            .format(user["firstname"], user["lastname"]))
    else:
        command.append("--groups")
        command.append(user["groups"])
    subprocess.call(command)
