from flask import Flask, abort, request
import hashlib
from hashlib import md5
app = Flask(__name__)

owners = []
chargers = []

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

def authorization(validate):
    try:
        if searchUser(validate):
            if((getUser(validate)).password == validate.password):
                return True
        return False
    except:
        return False


@app.route('/newUser', methods = ['POST'])
def processingUser():
    global owners
    try:
        user = request.form('username')
        tempPassword = request.form('password')
        password = hashlib.md5(tempPassword.encode('utf8')).hexdigest()
        tempUser = owner(user, password)
        if(searchUser(tempUser)):
            abort(409, "This user alrady exists" )
        else:
            owners += [tempUser]
    except:
        return abort(400, "Incomplete form")


@app.route('/newCharger', methods = ['POST'])
def processingCharger():
    global chargers
    try:
        localVar = request.form['local']
        isActiveVar = request.form['isActive']
        username = request.get_json()['whoOwns']['username']
        password = request.get_json()['whoOwns']['password']
        tempUser = owner(username, password)
        if(authorization(tempUser)):
            newCharger = charger(localVar, isActiveVar, tempUser)  
            getUser(tempUser).ownerChargers += [newCharger]
            chargers += [newCharger]
        else:
            return abort(401, "User  not authorized")
    except:
        return abort(400, "Incomplete form")



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


