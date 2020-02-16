#!/usr/bin/python3

import os, sys
import json # to get data from POST only forms
import urllib.request
import re
import platform
import subprocess

# This file is responsible for creating a flask Web App UI 
#-----------------------------DEPENDENCIES-----------------------------#
import flask
from flask import Flask, templating, render_template, request, redirect
import socket # used to get local network exposible IP

import emailAgent # need to call functions
class WebApp():
    def __init__(self, textFunction, emailFunction):
        self.emailAgent = emailAgent.emailAgent(display_contacts=True)
        self.host_ip = self.getIP()
        self.host_port = '5000' # port 5000 allowed through firewall
        self.host_address = 'http://' + self.host_ip + ':' + self.host_port
        self.app = Flask(__name__)
        self.app.static_folder = "templates/stylesheets" # change location of where the css stylesheets are
        self.sites = {
            "landingpage"   :   '/',
            "textpage"      :   '/textpage',
            "emailpage"     :   '/emailpage',
            "aboutpage"     :   '/aboutpage',
            "sidebarpage"   :   '/sidebarpage'
        }
        self.formSites = {
            "textForm"      :   '/textForm',
            "emailForm"      :   '/emailForm'
        }
        self.debugOn = False

        # create all sites to begin with
        self.initializingStatus = True
        self.generateSites()
        self.generateFormResultsSites()
        self.printSites() # will only print if debug mode is on
        self.initializingStatus = False

        # start up the web app
        self.app.run(host=self.host_ip, port=self.host_port, debug=self.debugOn)
    
    def getIP(self):
        myPlatform = platform.system()
        if myPlatform == "Windows":
            hostname = socket.gethostname()
            IPAddr = socket.gethostbyname(hostname)
            return IPAddr
        elif myPlatform == "Linux":
            ipExpr = r'inet ([^.]+.[^.]+.[^.]+.[^\s]+)'
            output = subprocess.check_output("ifconfig").decode()
            matches = re.findall(ipExpr, output)
            for ip in matches:
                print("Found ip: {0}".format(ip))
                return ip


    def generateSites(self):
        '''
            This function is a wrapper around all the other functions which actually create pages.
            Hence, by calling this function all sites will be initialized.
        '''
        # wrap pages in generateSites function so that 'self' can be used
        # for each function render the sidebar so that there is a single source of truth for its design
        @self.app.route(self.sites['landingpage'], methods=["GET", "POST"])
        def createMainPage():
            return render_template("mainPage.html", title="Texting App Main Page", links=self.sites)

        @self.app.route(self.sites['textpage'], methods=["GET", "POST"])
        def createTextPage():
            contactList = self.emailAgent.printContactListPretty(printToTerminal=False)
            return render_template("textPage.html", title="Texting App Texting Page", 
                links=self.sites, forms=self.formSites, contacts=contactList)

        @self.app.route(self.sites['emailpage'], methods=["GET", "POST"])
        def createEmailPage():
            self.emailAgent.updateContactList()
            contactList = self.emailAgent.printContactListPretty(printToTerminal=False)
            return render_template("emailPage.html", title="Texting App Email Page", 
                links=self.sites, forms=self.formSites, contacts=contactList)

        @self.app.route(self.sites['aboutpage'], methods=["GET", "POST"])
        def createAboutPage():
            return render_template("aboutPage.html", title="Texting App About Page", links=self.sites)

        @self.app.route('/crash')
        def test():
            raise Exception()
    
    # form submissions get posted here (only accessible)
    def generateFormResultsSites(self):
        formData = {}
        @self.app.route(self.formSites['textForm'], methods=['POST'])
        def createTextForm():
            # if form is given data
            if (not self.initializingStatus):
                url = self.host_address + self.formSites['textForm']
                formData = flask.request.get_json()
                # collect all form information
                firstName = formData['firstName']
                lastName = formData['lastName']

                # login info error-checking
                try:
                    email = formData['emailAddress']
                    password = formData['password']
                except Exception as e:
                    # if there is an error just use the default sender/receiver
                    self.emailAgent.setDefaultState(True)

                # check if receive if sending/receiving message form
                if (formData['task'] == "sending"):
                    message = formData['message']
                    print("IMPLEMENT SEND")
                    receiver_contact_info = emailer.get_receiver_contact_info(firstName, lastName)
                    
                    self.emailAgent.sendMsg(receiver_contact_info, sendMethod='text')
                
                elif (formData['task'] == "receiving"):
                    print("IMPLEMENT RECEIVE")
                    # toPrint = self.emailAgent.getPrintedString()
                    # print(toPrint)
                
                elif (formData['task'] == "adding-contact"):
                    carrier = formData['carrier']
                    phoneNumber = formData['phoneNumber']
                    self.emailAgent.add_contacts_to_contacts_list(firstName, lastName, email, carrier, phoneNumber)
                else:
                    raise Exception("UNKNOWN TASK")

                # return to original site
                return redirect(self.host_address + self.sites['textpage'])
            
            # if dont return elsewhere, use blank page
            return render_template("basicForm.html")
        


    def printSites(self):
        '''
            Helper function to tell user the location of each site
        '''
        print("\nAll the created sites are: \n")
        for site in self.sites.keys():
            print("{0}{1}".format(self.host_address, self.sites[site]))
        print() # newline



if __name__ == "__main__":
    textFn = lambda: print("texting")
    emailFn = lambda: print("emailing")
    ui = WebApp(textFn, emailFn)