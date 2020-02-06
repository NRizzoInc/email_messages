#!/usr/bin/python3

# This file is responsible for creating a flask Web App UI 
#-----------------------------DEPENDENCIES-----------------------------#
import flask
from flask import Flask, templating, render_template, request
import socket # used to get local network exposible IP

class WebApp():
    def __init__(self, textFunction, emailFunction):
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
        # dictionary containing the buttons and their associated values in the html
        self.buttons = {
            "emailButtons"  : {
            },
            "textButtons"   : {
                "send"      :   "Send Text"
            }
            
        }
        self.debugOn = False

        #-----------SETUP FUNCTIONS TO BE CALLED BY BUTTONS-------#
        self.textFunction = textFunction
        self.emailFunction = emailFunction

        # create all sites to begin with
        self.generateSites()
        self.printSites() # will only print if debug mode is on

        # start up the web app
        self.app.run(host=self.host_ip, port=self.host_port, debug=self.debugOn)
    
    def getIP(self):
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        return IPAddr

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
            # upon POST requests (which occur when clicking buttons) do this...
            if (request.method == "POST"):
                # self.textFunction()
                return render_template("textPage.html", title="Texting App Texting Page", links=self.sites, buttons=self.buttons)

            return render_template("textPage.html", title="Texting App Texting Page", links=self.sites, buttons=self.buttons)

        @self.app.route(self.sites['emailpage'], methods=["GET", "POST"])
        def createEmailPage():
            if (request.method == "POST"):
                self.emailFunction()
            return render_template("emailPage.html", title="Texting App Email Page", links=self.sites, buttons=self.buttons)

        @self.app.route(self.sites['aboutpage'], methods=["GET", "POST"])
        def createAboutPage():
            return render_template("aboutPage.html", title="Texting App About Page", links=self.sites)

        @self.app.route('/crash')
        def test():
            raise Exception()
    
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