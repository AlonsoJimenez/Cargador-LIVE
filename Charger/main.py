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

def changeStatus(local, charger):
    global chargers
    global owners
    for xCharger in chargers:
        if(xCharger.equals(local)):
            xCharger.occupied = not xCharger.occupied
    
def tempUserFinder(varUsername):
    global owners
    for xOwner in owners:
        if xOwner.username == varUsername:
            return xOwner
    return None

def findCharger(local):
    global chargers
    for xCharger in chargers:
        if(xCharger.equals(local)):
            return xCharger
    return None

def makeJsonList(listVar):
    result = []
    for ob in listVar:
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
            if(xCharger == location):
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
            print(owners)
            print(tempUser.ownerChargers)
            print(chargers)
            return make_response("OK", 200)
    except:
        return abort(400, "Incomplete form")

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
            tempUserFinder(username).ownerChargers += [localVar]
            chargers += [newCharger]
            return make_response("OK", 200)
    except:
        return abort(400, "Incomplete form")


@app.route('/chargerOcupied', methods = ['PUT'])
@authAu
def changeCharger():
    global chargers
    try:
        localization = eval(request.form['local'])
        xCharger = findCharger(localization)
        if(request.authorization.username == xCharger.owner):
            changeStatus(localization, xCharger)
            return make_response("Ok", 200) 
        else:
            return abort(401, "User not authorized")
    except:
        return abort(400, "Invalid form information")

@app.route('/deactivate', methods = ['PUT'])
@authAu
def deactivate():
    global chargers
    try:
        localVar = eval(request.form['local'])
        tempCharger = findCharger(localVar)
        tempCharger.active = not tempCharger.active
        return make_response("OK", 200)
    except:
        return abort(400, "Unable to process request")

@app.route('/changePassword', methods = ['PUT'])
@authAu
def changePassword():
    global owners
    try:
        tempPassword = request.form['password']
        newPassword = hashlib.md5(tempPassword.encode('utf8')).hexdigest()
        user = tempUserFinder(request.authorization.username)
        user.password = newPassword
        return make_response("ok", 200)
    except:
        return abort(400, "Unable to process request")


@app.route('/getNetwork', methods = ['GET'])
def getNetwork():
    global chargers
    try:
        return make_response(makeJsonList(chargers), 200)
    except:
        return abort(400, "Unable to process request")


@app.route('/userChargers', methods = ['GET'])
def userChargers():
    global chargers
    try:
        user = tempUserFinder(request.form['username'])
        result = []
        for xLocal in user.ownerChargers:
            result += [findCharger(xLocal)]
        return make_response(makeJsonList(result), 200)
    except:
        return abort(400, "Unable to process request")


@app.route('/getCharger', methods = ['GET'])
def getCharger():
    global chargers
    try:
        local = findCharger(request.form['local'])
        return make_response(makeJsonList([local]), 200)
    except:
        return abort(400, "Unable to process request")


@app.route('/deleteUser', methods = ['DELETE'])
@authAu
def deleteUser():
    global chargers
    global owners
    try:
        user = request.authorization.username
        userChargers = tempUserFinder(user).ownerChargers
        for xCharger in userChargers:
            chargers.remove(findCharger(xCharger))
        owners.remove(tempUserFinder(user))
        return make_response("Ok", 200)
    except:
        return abort(400, "Unable to process request")


class owner:

    username = ""
    password = ""
    ownerChargers = []

    def __init__(self, varUser, varPassword, ownerChargersVar = []):
        self.username = varUser
        self.password = varPassword
        self.ownerChargers = ownerChargersVar

    def getChargers(self,):
        return self.ownerChargers

class charger:

    localization = []
    occupied = True
    active = True
    owner = None

    def equals(self, local):
        if self.localization == local:
            return True
        return False

    def __new__(cls, local, isActive, whoOwns, isOccupied = True):
        global owners
        
        if(local != None and isActive != None and whoOwns != None):
            instance = super(charger, cls).__new__(cls)
            instance.localization = local
            instance.active = isActive
            instance.owner = whoOwns
            instance.occupied = isOccupied
            return instance
        else:
            return "Error in charger arguments"

    def changeActivity(self,):
        self.occupied = not self.occupied

    def changeStatus(self,):
        self.active = not self.active


if __name__ =="__main__":
    app.run()