#!/usr/bin/python3

import json
import csv
import subprocess
import sys
from unidecode import unidecode
from datetime import datetime

class WrongFileType(Exception):
    pass

def main():
    try:
        filename = sys.argv[1]
        if "json" in filename:
            processJson(filename)
        elif "csv" in filename:
            processCsv(filename)
        else:
            raise  WrongFileType("ERROR: Wrong type of file")
    except IndexError:
        raise IndexError("usage: {} <json file>".format(sys.argv[0].split('/')[-1]))
    except:
        raise

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

# returns the number of seconds since the epoch from the date
def dateToSeconds(dateStr):
    try:
        # converts string to date object
        date = datetime.strptime(dateStr, "%y/%m/%d")
        # returns seconds since epoch
        return int(datetime.timestamp(date))
    except ValueError:
        raise ValueError("Wrong format for date. It should be yy/mm/dd")
    except:
        raise



def processJson(filename):
    # reads the JSON file
    batch = dict()
    try:
        with open(filename, "r") as f:
            batch = json.load(f)
        # checks if users have set first- and lastnames
        # (necessary for setting def. username and password)
        for user in batch.values():
            if ("firstname" not in user or "lastname" not in user
                or user["firstname"] == "" or user["lastname"] == ""):
                raise ValueError("One or more users do not have a first- or lastname. Please check.")
    except: # handled in one place
        raise

    # builds and runs the command for each user
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
        if ("expire" in user and  user["expire"] != ""):
            try:
                command.append("--expire")
                command.append(str(dateToSeconds(user["expire"])))
            except ValueError as e:
                print("ERROR: User {} {}: "
                     .format(user["firstname"], user["lastname"])
                     + e.args[0])
                continue
        if ("groups" in user and  user["groups"] != ""):
            command.append("--groups")
            command.append(user["groups"])
        else:
            print("WARNING: user {} {} has no group(s) assigned"
                .format(user["firstname"], user["lastname"]))
        subprocess.call(command)
        # print(" ".join(command))

def processCsv(filename):
    # reads the CSV file
    try:
        with open(filename, "r") as f:
            reader = csv.reader(f, delimiter=';')
            users = list(reader)
        # checks if users have set first- and lastnames
        # (necessary for setting def. username and password)
        for user in users:
            if user[0] == "" or user[1] == "":
                raise ValueError("One or more users do not have a first- or lastname. Please check.")
    except: # handled in one place
        raise

    # builds and runs the command for each user
    for user in users:
        # sets username and def. one-use-password
        userPass = createUserPass(user[0], user[1])
        username = userPass[0]
        password = userPass[1]
        # command minimum parameters
        command = [
        "pveum", "useradd", username, "--password", password,
        "--firstname", user[0],
        "--lastname", user[1]
        ]
        # sets optional parameters
        if user[2] != "":
            command.append("--email")
            command.append(user[2])
        if (user[3] != ""):
            try:
                command.append("--expire")
                command.append(str(dateToSeconds(user[3])))
            except ValueError as e:
                print("ERROR: User {} {}: ".format(user[0], user[1])
                     + e.args[0])
                continue
        if user[4] != "":
            command.append("--groups")
            command.append(user[4])
        else:
            print("WARNING: user {} {} has no group(s) assigned"
                .format(user[0], user[1]))
        subprocess.call(command)
        # print(" ".join(command))
try:
    main()
except IndexError as e:
    print("ERROR: " + e.args[0])
except WrongFileType as e:
    print("ERROR: " + e.args[0])
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
except TypeError as e:
    print("ERROR: " + e.args[0])
except csv.Error:
    print("ERROR: An error occurred while reading the file")
