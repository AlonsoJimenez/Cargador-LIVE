from flask import Flask
fron flask import abort, request, jsonify, make_response, json
import hashlib
from hashlib import md5
from functools import wraps
import json
from flask_cors import CORS

app = Flask(__name__)

CORS(app)
#la linea inferior de codigo tiene el proposito de permitir saltar los protocolos CORS y realizar pruebas con una pagina en Node JS
cors = CORS(app, resources = {r"/*": {"origins" : "*"}})

#owners y chargers son las listas usadas como base de datos del programa
#pueden ser mejoradas en versiones posteriores
owners = []
chargers = []


#funcion que sirve como wrap para los metodos que requieran autorizacion
#puede devolver la funcion del metodo http o un error
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


'''
las funciones: tempUserFinder, findCharger, getUser, searchUser, locationUsed, authorization,
podran ser optimizadas para ser incluidas con una busqueda binaria u otro algoritmo optimo para una busqueda 
mas rapida de los items
'''

#funcion cambia el estado y lo actualiza para el acceso de informacion
def changeStatus(local, charger):
    global chargers
    global owners
    for xCharger in chargers:
        if(xCharger.equals(local)):
            xCharger.occupied = not xCharger.occupied

#funcion hace busqueda de usuario por medio del username    
def tempUserFinder(varUsername):
    global owners
    for xOwner in owners:
        if xOwner.username == varUsername:
            return xOwner
    return None

#encuentra cargador por medio del voltaje deseado
def findVoltage(voltage):
    global chargers
    result = []
    for xCharger in chargers:
        if(xCharger.voltage==voltage):
            result+=[xCharger]
    return result

#encuentra cargador por medio del tipo de cargador
def findChargerType(typeCharger):
    global chargers
    result = []
    for xCharger in chargers:
        if(xCharger.chargerType==typeCharger):
            result+=[xCharger]
    return result

#encuentra cargador por medio de la lista de cordenadas del cargador
def findCharger(local):
    global chargers
    for xCharger in chargers:
        if(xCharger.equals(local)):
            return xCharger
    return None

#funcion reibe una lista cualquiera y cambia a un String con formato tipo JSON
def makeJsonList(listVar):
    result = []
    for ob in listVar:
        result += [ob.__dict__]
    return(json.dumps(result))

#encuentra ususario por medio de la instacia de otro usuario con mismo nombre de usuario
#un usuario cualquiera no puede crear o instanciar una cuenta con nombre de usaurio repetido la funcion es auxiliar
def getUser(user):
    for xOwner in owners:
        if xOwner.username == user.username:
            return xOwner
    return None

#funcion utiliza el usuario para buscar el ususario en la base de datos y devuelve True en caso de tener uno con el mismo username
def searchUser(user):
    name = user.username
    for xOwner in owners:
        if(xOwner.username == name):
            return True
    return False

#devuelve True en caso de que la localizacion del parametro este en la base de datos
def locationUsed(location):
    global owners
    for xOwner in owners:
        for xCharger in xOwner.ownerChargers:
            if(xCharger == location):
                return True
    return False

#funcion auxiliar para verificar el usuario y la contrasena
#verifica la existencia del usuario y la contrasena es encriptada para poder verificarla con la base de datos
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

#funcion recibe la informacion para crear nuevos usuarios
#la funcion esta protegida contra excepciones de nombre de usuario repetido, formulario invalido y errores de proceso del servidor
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

#recibe informacion para crear un nuevo cargador
#esta verificada contra varios errores
#necesita verifiacion de tipo Basic Auth
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

#recibe informacion para actualizar el estado ocupado del cargador
#esta verificada contra varios errores
#necesita verifiacion de tipo Basic Auth
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

#funcion recibe informacion para desactivar el uso del cargador seleccionado
#esta verificada contra varios errores
#necesita verifiacion de tipo Basic Auth
@app.route('/deactivate', methods = ['PUT'])
@authAu
def deactivate():
    global chargers
    try:
        localVar = eval(request.form['local'])
        tempCharger = findCharger(localVar)
        if(request.authorization.username == tempCharger.owner):
            tempCharger.active = not tempCharger.active
            return make_response("Ok", 200) 
        else:
            return abort(401, "User not authorized")
    except:
        return abort(400, "Unable to process request")

#funcion actualiza la contrasena del usuario, igualmente la conrsana es encriptada
#esta verificada contra varios errores
#necesita verifiacion de tipo Basic Auth
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

#funcion actualiza la foto de un cargador especifico
#esta verificada contra varios errores
#necesita verifiacion de tipo Basic Auth
@app.route('/changePic', methods = ['PUT'])
@authAu
def changePicture():
    global chargers
    try:
        localVar = eval(request.form['local'])
        tempCharger = findCharger(localVar)
        newPic = request.form['picture']
        if(request.authorization.username == tempCharger.owner):
            tempCharger.picture = newPic
            return make_response("Ok", 200) 
        else:
            return abort(401, "User not authorized")
    except:
        return abort(400, "Unable to process request")

#funcion actualiza referencia de un cargadppr especifico
#esta verificada contra varios errores
#necesita verifiacion de tipo Basic Auth
@app.route('/changeReference', methods = ['PUT'])
@authAu
def changeReference():
    global chargers
    try:
        localVar = eval(request.form['local'])
        tempCharger = findCharger(localVar)
        newRef = request.form['reference']
        if(request.authorization.username == tempCharger.owner):
            tempCharger.reference = newRef
            return make_response("Ok", 200) 
        else:
            return abort(401, "User not authorized")
    except:
        return abort(400, "Unable to process request")

#funcion actualiza tipo de cargador del mismo
#esta verificada contra varios errores
#necesita verifiacion de tipo Basic Auth
@app.route('/changeType', methods = ['PUT'])
@authAu
def changeType():
    global chargers
    try:
        localVar = eval(request.form['local'])
        tempCharger = findCharger(localVar)
        newType = request.form['chargerType']
        if(request.authorization.username == tempCharger.owner):
            tempCharger.chargerType = newType
            return make_response("Ok", 200) 
        else:
            return abort(401, "User not authorized")
    except:
        return abort(400, "Unable to process request")

#funcion actualiza los servicios disponibles en el cargador
#esta verificada contra varios errores
#necesita verifiacion de tipo Basic Auth
@app.route('/changeServices', methods = ['PUT'])
@authAu
def changeOtherServices():
    global chargers
    try:
        localVar = eval(request.form['local'])
        tempCharger = findCharger(localVar)
        newServices = request.form['otherServices']
        if(request.authorization.username == tempCharger.owner):
            tempCharger.otherServices = newServices
            return make_response("Ok", 200) 
        else:
            return abort(401, "User not authorized")
    except:
        return abort(400, "Unable to process request")

#funcion actualiza el voltaje del cargador
#esta verificada contra varios errores
#necesita verifiacion de tipo Basic Auth
@app.route('/changeVoltage', methods = ['PUT'])
@authAu
def changeVoltage():
    global chargers
    try:
        localVar = eval(request.form['local'])
        tempCharger = findCharger(localVar)
        newVoltage = eval(request.form['otherServices'])
        if(request.authorization.username == tempCharger.owner):
            tempCharger.voltage = voltage
            return make_response("Ok", 200) 
        else:
            return abort(401, "User not authorized")
    except:
        return abort(400, "Unable to process request")

#funcion devuelve toda la informacion publica de la red de cargadores en el mapa
@app.route('/getNetwork', methods = ['GET'])
def getNetwork():
    global chargers
    try:
        data = makeJsonList(chargers)
        response = app.response_class(
        response=data,
        status=200,
        mimetype='application/json'
    )
        return response
    except:
        return abort(400, "Unable to process request")

#funcion realiza una busqueda de cargadores en la red por usuario y devuelve su informacion
#es de acceso publico
@app.route('/userChargers', methods = ['GET'])
def userChargers():
    global chargers
    try:
        user = tempUserFinder(request.form['username'])
        result = []
        for xLocal in user.ownerChargers:
            result += [findCharger(xLocal)]
        response = app.response_class(
        response=makeJsonList(result),
        status=200,
        mimetype='application/json'
        )
        return response
    except:
        return abort(400, "Unable to process request")

#funcion realiza una busqued de un solo cargador por medio de la localizacion y luego devuelve la informacion
#la funcion es de acceso publico
@app.route('/getCharger', methods = ['GET'])
def getCharger():
    global chargers
    try:
        local = findCharger(request.form['local'])
        response = app.response_class(
        response=makeJsonList([local]),
        status=200,
        mimetype='application/json'
        )
        return response
    except:
        return abort(400, "Unable to process request")

#funcion realiza una busqued de los cargadores por medio de tipo de cargador
#la funcion es de acceso publico
@app.route('/type', methods = ['GET'])
def typeFinder():
    global chargers
    try:
        chargerType = findChargerType(request.form['type'])
        response = app.response_class(
        response=makeJsonList(chargerType),
        status=200,
        mimetype='application/json'
        )
        return response
    except:
        return abort(400, "Unable to process request")

#funcion realiza una busqued de los cargadores por medio de voltaje
#la funcion es de acceso publico
@app.route('/voltage', methods = ['GET'])
def voltage():
    global chargers
    try:
        voltage = findVoltage(request.form['voltage'])
        response = app.response_class(
        response=makeJsonList(voltage),
        status=200,
        mimetype='application/json'
        )
        return response
    except:
        return abort(400, "Unable to process request")

#funcion realiza la busqueda de un usuario para luego eliminarlo
#requiere autorizacion
#esta verificado contra excepciones de procesamiento y formulario incompleto
#realiza tambien la eliminacion de los cargadores del usuario
#la funcion puede ser optimizada por medio de mejores y mas adecuados aloritmos de busqueda
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

#objeto de tipo usuario, owner el nombre ya que sera dueno de cargadores ingresados por el al sistema
class owner:

    username = ""
    password = ""
    ownerChargers = []

    #funcion para la instanciacion
    def __init__(self, varUser, varPassword, ownerChargersVar = []):
        self.username = varUser
        self.password = varPassword
        self.ownerChargers = ownerChargersVar

    #funcion es un getter de los cargadores del mismo
    def getChargers(self,):
        return self.ownerChargers

#objeto de tipo cargador
class charger:

    localization = []
    voltage = 0
    chargerType = ""
    picture = ""
    reference = ""
    otherServices = ""
    occupied = True
    active = True
    owner = None

    #funcion realiza una comparacion de cargadores por medio de un dato que en teoria es unico (la localizaion)
    def equals(self, local):
        if self.localization == local:
            return True
        return False

    #funcion instancia bajo condiciones adecuadas el cargador
    def __new__(cls, local, isActive, whoOwns, isOccupied = True):
        global owners
        #recuerde al usuario sin importar que sea por medio de RestAPIS o por consola debe incluir argumentos de la instancia
        if(local != None and isActive != None and whoOwns != None):
            instance = super(charger, cls).__new__(cls)
            instance.localization = local
            instance.active = isActive
            instance.owner = whoOwns
            instance.occupied = isOccupied
            return instance
        else:
            return "Error in charger arguments"

    #cambia el estado del objeto entre ocupado y desocupado
    def changeActivity(self,):
        self.occupied = not self.occupied

    #cambia estado del objeto entre activado y desactivado
    def changeStatus(self,):
        self.active = not self.active

#codigo inferior corre el programa
if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)