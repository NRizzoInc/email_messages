"""
    \n@File: Responsible for maintaing the "users" collection
"""

#------------------------------STANDARD DEPENDENCIES-----------------------------#
import json
import pickle, copyreg, ssl # for serializing User objects (SSL obj requires more work)
import uuid

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from pymongo import MongoClient, collection
from bson.binary import Binary # for serializing/derializing User objects

#--------------------------------OUR DEPENDENCIES--------------------------------#
from backend.src import utils
from .databaseBaseClass import DatabaseBaseClass

class UsersCollectionManager(DatabaseBaseClass):
    def __init__(self):
        """
            \n@Brief: This class is responsible for managing the user's collection
            \n@Note: Inheret from DatabaseBaseClass which gives it alot of util functions and self variables
        """
        # Inheret all functions and 'self' variables
        super().__init__()

    def createSafeCookieId(self):
        """Creates UUID for users"""
        # do-while loop to make sure non-colliding unique id is made
        while True:
            # https://docs.python.org/3/library/uuid.html -- safe random uuid
            userToken = str(uuid.uuid4())
            inUse = self.isIdInUse(userToken)
            if not inUse: break # leave loop once new id is found
            else: print(f"userToken '{userToken}' is already taken")
        return userToken

    def _addUserToColl(self, userToken, username, password, userObj):
        """
            \n@Brief: High level api function call to add a user to the database
            \n@Param: userToken - The user's unique safe id (aka id)
            \n@Param: username - The user's chosen username
            \n@Param: password - The user's chosen password
            \n@Param: userObj - Reference to the instantiated userObj
        """
        newUser = {
            "id": userToken,
            "username": username,
            "password": password,
            "User": self._serializeObj(userObj) if userObj != None else None # need to serialize object for storage
        }
        self._replaceDataById(self.usersColl, userToken, newUser)

    def isUsernameInUse(self, usernameToTest:str):
        usernameExists = self._docExists(self.usersColl, {"username": usernameToTest})
        # print(f"usernameExists: {usernameExists}")
        return usernameExists
    
    def isIdInUse(self, idToTest:str):
        idExists = self._docExists(self.usersColl, {"id": idToTest})
        # print(f"idExists: {idExists}")
        return idExists

    def getIdByUsername(self, username)->str():
        """
            \n@Param: username - The username matching the id you are looking for
            \n@Return: The corresponding id
            \n@Note: Useful if chained with other functions that require id (i.e. 'findUserById()')
        """
        matches = list(self.usersColl.find({"username": username}))
        matchId = list(filter(self.filterLocalhost(), matches))[0]["id"]
        return matchId

    def findUserById(self, userToken, UserObjRef):
        """
            \n@Param: userToken - The user's unique token id
            \n@Param: UserObjRef - reference to the constructor for the User object
            \n@Return: The 'User' object (None if 'User' DNE or unset)
        """
        userDoc = self._getDocById(self.usersColl, userToken)
        return self._createUserObjIfDNE(userDoc, UserObjRef)

    def countNumUsernameMatch(self, username):
        return self.usersColl.find({"username": username}).count()

    def getUserByUsername(self, username, UserObjRef):
        """
            \n@Param: username: The username of the user's account
            \n@Param: UserObjRef - reference to the constructor for the User object
            \n@Returns: None if username does not exist
        """
        userDoc = self._getDocByUsername(self.usersColl, username)
        return self._createUserObjIfDNE(userDoc, UserObjRef)

    def _createUserObjIfDNE(self, userDoc, UserObjRef):
        """
            \n@Brief: Get the User object referenced in the document. If it doesn't exist, create one
            \n@Param: userDoc - The dictionary containing the information belonging to a specific user
            \n@Param: UserObjRef - reference to the constructor for the User object
            \n@Returns: The User object associated with the document (creates one if not already made/set)
            \n@Note: Good if paired with '__checkIfUserValid'
        """
        userObj = self.__checkIfUserValid(userDoc)
        userId = userDoc["id"]
        return userObj if userObj != None else UserObjRef(userId)

    def _createUserDocIfUsernameDNE(self, username, id="", password:str=""):
        """
            \n@BRief: Helper function that creates a new user in the database if username not found
            \n@Param: username - the username to search for
            \n@Param: id - (optional) The id to try to assign to the user if dne. WARNING: only use for cli
            \n@Param: password - (optional) If username does not exit, user this password for the user
            \n@Note: A user doc in the database contains id, username, password, and User object
        """
        usernameExists = self.isUsernameInUse(username)
        idInUse = self.isIdInUse(id)
        uuid = id if not idInUse else self.createSafeCookieId()
        self._addUserToColl(uuid, username, password, None)

    def _createUserDocIfIdDNE(self, id, username="", password:str=""):
        """
            \n@BRief: Helper function that creates a new user in the database if username not found
            \n@Param: id - the user's id to search for
            \n@Param: username - (optional) The username to try to assign to the user if dne
            \n@Param: password - (optional) If username does not exit, user this password for the user
            \n@Note: A user doc in the database contains id, username, password, and User object
            \n@Return: True if already exists, false if had to create it
        """
        idInUse = self.isIdInUse(id)
        if idInUse: return True
        username = "" if username == "" or username == None or self.isUsernameInUse(username) else username
        self._addUserToColl(id, username, password, None)
        return False

    def __checkIfUserValid(self, userDoc:dict):
        """
            \n@Brief: Helper function that checks if the 'User' obj within the document has been set and is valid
            \n@Param: userDoc - The dictionary containing the information belonging to a specific user
            \n@Return: The User object 
        """
        if utils.keyExists(userDoc, "User") and userDoc["User"] != None:
            serializedUserObj = userDoc["User"]
            userObj = self._deserializeData(serializedUserObj)
        else: userObj = None
        return userObj

    def getPasswordFromUsername(self, username:str)->str():
        """
            \n@Param: username - The password to find's username
            \n@Returns: The matching password 
        """
        matches = list(self.usersColl.find({"username": username}))
        actualPassword = list(filter(self.filterLocalhost(), matches))[0]["password"]
        return actualPassword

    def getPasswordFromId(self, myId:str)->str():
        """
            \n@Param: myId - The password to find's id
            \n@Returns: The matching password (or "" if not yet set)
        """
        match = self._getDocById(self.usersColl, myId)
        username = match["password"] if utils.keyExists(match, "password") else ""
        return username

    def updateUserObjById(self, myId:str, updatedUserObj:object)->dict():
        """
            \n@Brief: Updates the 'User' object in the document corresponding to the id
            \n@Param: myId - The UUID of the user to update
            \n@Param: updatedUser - The User object to replace the existing one with
            \n@Returns: An instance of UpdateResult
        """
        query = {"id": myId}
        # https://docs.mongodb.com/manual/reference/operator/update/#id1 -- different update commands
        # $set = set matching field
        serializedUpdatedObj = self._serializeObj(updatedUserObj)
        toUpdateWith = {"$set": {"User": serializedUpdatedObj}}
        return self.usersColl.update_one(query, toUpdateWith)

    def setUsernameById(self, myId:str, username:str):
        """
            \n@Brief: Sets the username in the database for the user with 'myId'
            \n@Param: myId - The id of the user whose username you want to set
            \n@Param: username - The username to set
            \n@Note: Probably only useful for command line uses
            \n@Returns: An instance of UpdateResult
        """
        query = {"id": myId}
        toUpdateWith = {"$set": {"username": username}}
        return self.usersColl.update_one(query, toUpdateWith)

    def setPasswordById(self, myId:str, password:str):
        """
            \n@Brief: Sets the password in the database for the user with 'myId'
            \n@Param: myId - The id of the user whose username you want to set
            \n@Param: password - The password to set
            \n@Note: Probably only useful for command line uses
            \n@Returns: An instance of UpdateResult
        """
        query = {"id": myId}
        toUpdateWith = {"$set": {"password": password}}
        return self.usersColl.update_one(query, toUpdateWith)

    def getUsernameById(self, myId:str)->str():
        """
            \n@Brief: Gets the username in the database for the user with 'myId'
            \n@Param: myId - The id of the user whose username you want to set
            \n@Returns: The username belonging to the ID (empty string if not set)
        """
        match = self._getDocById(self.usersColl, myId)
        username = match["username"] if utils.keyExists(match, "username") else ""
        return username

