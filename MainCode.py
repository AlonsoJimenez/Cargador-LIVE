from flask import Flask, abort, request
import hashlib
from hashlib import md5
app = Flask(__name__)

def getUser(user):
    for xOwner in owners:
        if xOwner.username == user.username:
            return xOwner
    return None

def searchUser(user):
    name = user.username
    for xOwner in owners:
        if xOwner.username == name
        return True
    return False

def authorization(validate):
    try:
        if searchUser(validate):
            if((getUser(validate)).password == validate.password):
                return True
        return False

owners = {}
chargers = []

@app.route('/newUser', methods = ['POST'])
def processingUser():
    try:
        user = request.form('username')
        password = hashlib.md5(b request.form('password')).hexdigest()
        tempUser = owner(user, password)
        if(searchUser(tempUser)):
            abort(409, "This user alrady exists" )
        else:
            chargers += [tempUser]
    except:
        return abort(400, "Incomplete form")


@app.route('/newCharger', methods = ['POST'])
def processingCharger():
    try:
        localVar = request.form['local']
        isActiveVar = request.form['isActive']
        whoOwnsVar = request.form['whoOwns']


        charger(localVar, isActiveVar, whoOwnsVar)  
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
            return "Error in charger argguments"

    def changeActivity(self,):
        self.occupied = not self.occupied

    def changeStatus(self,):
        self.active = not self.active

if __name__ =="__main__":
    app.run()


