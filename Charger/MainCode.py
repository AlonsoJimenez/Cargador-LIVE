from flask import Flask, abort, request, jsonify, make_response
import hashlib
from hashlib import md5
from functools import wraps
import json

app = Flask(__name__)

owners = []
chargers = []

def authAu(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        tempUser = owner(auth.username, auth.password)
        if(authorization(tempUser)):
            return f(*args, **kwargs)
        else:
            return abort(401, "User not authorized")
    return decorated

def changeStatus(local, charger, username):
    global chargers
    global owners
    for xCharger in chargers:
        if(xCharger.equals(local)):
            xCharger.occupied = not xCharger.occupied
    for xOwner in owners:
        if(xOwner.username == username):
            for userCharger in xOwner.ownerChargers:
                if(userCharger.equals(local)):
                    userCharger.occupied = not userCharger.occupied

def findCharger(local):
    global chargers
    for xCharger in chargers:
        if(xCharger.equals(local)):
            return xCharger
    return None

def makeJsonList(list):
    result = []
    for ob in list:
        result += [ob.__dict__]
    return(json.dumps(result))

def getUser(user):
    for xOwner in owners:
        if xOwner.username == user.username:
            return xOwner
    return None

def searchUser(user):
    name = user.username
    for xOwner in owners:
        if(xOwner.username == name):
            return True
    return False

def locationUsed(location):
    global owners
    for xOwner in owners:
        for xCharger in xOwner.ownerChargers:
            if(xCharger.localization == location):
                return True
    return False

def authorization(validate):
    try:
        if searchUser(validate):
            tempPassword = validate.password
            tempPassword =  hashlib.md5(tempPassword.encode('utf8')).hexdigest()
            if((getUser(validate)).password == tempPassword):
                return True
        return False
    except:
        return False

@app.route('/newUser', methods = ['POST'])
def processingUser():
    global owners
    try:
        user = request.form['username']
        tempPassword = request.form['password']
        password = hashlib.md5(tempPassword.encode('utf8')).hexdigest()
        tempUser = owner(user, password)
        if(searchUser(tempUser)):
            return make_response("This user already exists", 409 )
        else:
            owners += [tempUser]
            return make_response("OK", 200)
    except:
        return abort(400, "Incomplete form")

@app.route('/chargerOcupied', methods = ['POST'])
@authAu
def changeCharger():
    global chargers
    try:
        localization = eval(request.form['local'])
        xCharger = findCharger(localization)
        if(request.authorization.username == xCharger.owner):
            changeStatus(localization, xCharger, request.authorization.username)
            return make_response("Ok", 200) 
        else:
            return abort(401, "User not authorized")
    except:
        return abort(400, "Invalid form information")

@app.route('/newCharger', methods = ['POST'])
@authAu
def processingCharger():
    global chargers
    try:
        localVar = eval(request.form['local'])
        if(locationUsed(localVar)):
            return make_response("Location has been already registered as charger", 400)
        else:
            isActiveVar = eval(request.form['isActive'])
            username = request.authorization.username
            newCharger = charger(localVar, isActiveVar, username)  
            getUser(owner(username, "ACCESS")).ownerChargers += [newCharger]
            chargers += [newCharger]
            return make_response("OK", 200)
    except:
        return abort(400, "Incomplete form")

@app.route('/getNetwork', methods = ['GET'])
def getNetwork():
    global chargers
    try:
        return(makeJsonList(chargers))
    except:
        return abort(400, "Unable to process request")

class owner:

    username = ""
    password = ""
    ownerChargers = []

    def __init__(self, varUser, varPassword):
        self.username = varUser
        self.password = varPassword

class charger:

    localization = []
    occupied = True
    active = True
    owner = None

    def equals(self, local):
        if self.localization == local:
            return True
        return False

    def __new__(cls, local, isActive, whoOwns):
        global owners
        
        if(local != None and isActive != None and whoOwns != None):
            instance = super(charger, cls).__new__(cls)
            instance.localization = local
            instance.active = isActive
            instance.owner = whoOwns
            return instance
        else:
            return "Error in charger arguments"

    def changeActivity(self,):
        self.occupied = not self.occupied

    def changeStatus(self,):
        self.active = not self.active


if __name__ =="__main__":
    app.run()