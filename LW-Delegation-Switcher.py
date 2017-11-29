""" A simple Studio Delegation Switcher for Livewire """

__product__     = "Livewire Simple Delegation Switcher"
__author__      = "Anthony Eden"
__copyright__   = "Copyright 2017, Anthony Eden / Media Realm"
__credits__     = ["Anthony Eden"]
__license__     = "GPL"
__version__     = "1.4.0"

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/libs")

import json
from LWRPClient import LWRPClient
import AxiaLivewireAddressHelper
import Tkinter as tk
import tkMessageBox
from functools import partial
import math
import requests
import thread

class Application(tk.Frame):

    # A list of all the source select buttons
    sourceButtons = []
    
    # The error message label widget
    errorLabel = None

    # The configurable text to put at the top of the main windows
    titleLabel = "Livewire Simple Delegation Switcher"

    # Store the Livewire Routing Protocol (LWRP) client connection here
    LWRP = None

    # Configuration parameters for the communication with the Device
    LWRP_IpAddress = None
    LWRP_PortNumber = 93
    LWRP_Password = None
    LWRP_OutputChannel = None
    LWRP_CurrentOutput = None
    LWRP_Sources = []

    # How many columns do we want?
    columnNums = 1

    # How many buttons in each column?
    columnButtonsEach = 0

    # How many buttons are in the current column?
    columnCurrentCount = 0

    # Which column are we currently rendering?
    columnCurrentNum = 0

    # Should we automatically check for version updates when the app starts up?
    autoCheckVersion = True

    newVersion = False

    def __init__(self, master = None):
        # Setup the application and display window
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.resizable(width = False, height = False)
        
        # Setup the application's icon - very important!
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)

        iconfile = os.path.join(application_path, "SwitchIcon.ico")

        try:
            self.root.iconbitmap(iconfile)
        except:
            # We don't care too much if the icon can't be included
            pass

        
        # Setup the main window for the application
        tk.Frame.__init__(self, master)
        self.grid(sticky = tk.N + tk.S + tk.E + tk.W)

        if self.setupConfig() is not True:
            self.setErrorMessage("ERROR: " + str(self.setupConfig()))

        else:
            connectionStatus, connection = self.connectLWRP()

            if connectionStatus is False:
                self.setErrorMessage("ERROR: " + str(connection))
        
        self.setupMainInterface()

        if self.autoCheckVersion is True:
            # Check for version updates in another thread
            thread.start_new_thread(self.versionCheck, ())

    def setupConfig(self):
        # Reads the 'config.json' file and stores the details in this class
        config = self.setupConfigRead('config.json')
        
        if config is False:
            return "Cannot parse configuration file 'config.json'"

        self.LWRP_IpAddress = config['DeviceIP']
        self.LWRP_OutputChannel = config['DeviceOutputNum']

        if "DevicePassword" in config and config['DevicePassword'] is not None:
            self.LWRP_Password = config['DevicePassword']

        if "Title" in config:
            self.titleLabel = config['Title']
        
        if "CheckUpdatesAuto" in config and config['CheckUpdatesAuto'] is False:
            self.autoCheckVersion = False

        for source in config['Sources']:
            if source['SourceNum'][:4] == "sip:":
                self.LWRP_Sources.append(
                    {
                        "ButtonLabel": source['Name'],
                        "LWNumber": None,
                        "LWMulticastNumber": None,
                        "LWSipAddress": source['SourceNum']
                    }
                )
            else:
                self.LWRP_Sources.append(
                    {
                        "ButtonLabel": source['Name'],
                        "LWNumber": int(source['SourceNum']),
                        "LWMulticastNumber": AxiaLivewireAddressHelper.streamNumToMulticastAddr(source['SourceNum']),
                        "LWSipAddress": None
                    }
                )
        
        if "Columns" in config:
            self.columnNums = int(config['Columns'])
            self.columnButtonsEach = int(math.ceil(len(self.LWRP_Sources) / self.columnNums))
        
        return True
    
    def setupConfigRead(self, filename):
        
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)

        filename = os.path.join(application_path, filename)
        
        try:
            Config_JSON = open(filename).read()
            return json.loads(Config_JSON)
        
        except Exception, e:
            print "EXCEPTION:", e
            return False

    def connectLWRP(self):
        # Tries to establish a connection to the LWRP on the specified device
        
        try:
            self.LWRP = LWRPClient(self.LWRP_IpAddress, self.LWRP_PortNumber)
        except Exception, e:
            print "EXCEPTION:", e
            return (False, "Cannot connect to LiveWire device")
        
        try:
            self.LWRP.login(self.LWRP_Password)
        except Exception, e:
            print "EXCEPTION:", e
            return (False, "Cannot login to device")

        # Find the current status of the output
        destinationList = self.LWRP.destinationData()
        self.LWRP_CurrentOutput = self.findOutputLWRP(destinationList, self.LWRP_OutputChannel)

        self.LWRP.destinationDataSub(self.callbackOutputsLWRP)

        return (True, self.LWRP)

    def findOutputLWRP(self, destinationList, destinationNumber):
        # Find the current output stream number for the specified output
        for destination in destinationList:
            if int(destination['num']) == destinationNumber and destination['attributes']['address'] is not None and destination['attributes']['address'][:4] == "sip:":
                # The active output, in Livewire SIP format
                return destination['attributes']['address']

            if int(destination['num']) == destinationNumber and destination['attributes']['address'] is not None and "." in destination['attributes']['address']:
                # The active output, in Multicast IP Address format
                return AxiaLivewireAddressHelper.multicastAddrToStreamNum(destination['attributes']['address'])
            
            elif int(destination['num']) == destinationNumber and destination['attributes']['address'] is not None and "." not in destination['attributes']['address']:
                # The active output, in Livewire Stream Number format
                return destination['attributes']['address']

            elif int(destination['num']) == destinationNumber:
                return None

        return False

    def callbackOutputsLWRP(self, data):
        # Find the current status of the output
        newSource = self.findOutputLWRP(data, self.LWRP_OutputChannel)

        if newSource is not None and newSource is not False:
            self.LWRP_CurrentOutput = newSource

        self.sourceBtnUpdate()
    
    def setupMainInterface(self):
        # Setup the interface with a list of source select buttons

        self.top = self.winfo_toplevel()
        self.top.rowconfigure(0, weight = 1)
        self.top.columnconfigure(0, weight = 1)
        
        if self.columnNums > 1:
            wrap = None
        else:
            wrap = 400

        # Title Label
        titleLabel = tk.Label(
            self,
            text = str(self.titleLabel),
            font = ("Arial", 24, "bold"),
            wraplength = wrap
        )
        titleLabel.pack()
        titleLabel.grid(
            column = 0,
            columnspan = self.columnNums,
            row = 0,
            sticky = ("N", "S", "E", "W"),
            padx = 50,
            pady = 5
        )

        # Create the label widget for error messages
        self.setErrorMessage()

        # Create the main menu
        menubar = tk.Menu()
        menubar.add_command(label = "About", command = self.about)
        menubar.add_command(label = "Updates", command = self.updates)
        menubar.add_command(label = "Quit!", command = self.close)
        self.top.config(menu = menubar)

        self.sourceBtnUpdate()

    def sourceBtnUpdate(self):
        # Update the status of all the source buttons on screen

        for sourceNum, sourceData in enumerate(self.LWRP_Sources):
            self.top.rowconfigure(self.columnCurrentCount + 1, weight = 1, pad = 20)
            
            if len(self.sourceButtons) >= sourceNum + 1:
                # Modify an existing button
                button = self.sourceButtons[sourceNum]

            else:
                # Setup a new button
                button = tk.Button(
                    self,
                    text = sourceData['ButtonLabel'],
                    font = ("Arial", 18, "bold"),
                    command = partial(self.sourceBtnPress, sourceNum)
                )

                # Assign the button to the grid
                button.grid(
                    column = self.columnCurrentNum,
                    row = self.columnCurrentCount + 1,
                    sticky = ("N", "S", "E", "W"),
                    padx = 50,
                    pady = 5
                )

                self.columnCurrentCount += 1

                if self.columnCurrentCount >= self.columnButtonsEach and self.columnCurrentNum < self.columnNums - 1:
                    self.columnCurrentCount = 0
                    self.columnCurrentNum += 1

                self.sourceButtons.append(button)

            if sourceData['LWSipAddress'] is not None and self.LWRP_CurrentOutput == sourceData['LWSipAddress']:
                # This channel is currently selected - SIP
                button.config(bg = "#FF0000", fg = "#FFFFFF")
            elif sourceData['LWNumber'] is not None and self.LWRP_CurrentOutput == sourceData['LWNumber']:
                # This channel is currently selected - multicast
                button.config(bg = "#FF0000", fg = "#FFFFFF")
            else:
                # This channel is not currently selected
                button.config(bg = "#FFFFFF", fg = "#000000")
    
    def sourceBtnPress(self, sourceNum):
        # Immediatly trigger a change to the destination/output
        if self.LWRP is None:
            # No active connection to LWRP Device
            self.setErrorMessage("Cannot change destination to button #"+str(sourceNum)+" - no connection to LWRP Device ")

        elif self.LWRP_Sources[sourceNum]['LWSipAddress'] is not None:
            # Sip-based addressing
            self.LWRP.setDestination(self.LWRP_OutputChannel, self.LWRP_Sources[sourceNum]['LWSipAddress'])

        elif self.LWRP_Sources[sourceNum]['LWMulticastNumber'] is not None:
            # Multicast-based addressing
            self.LWRP.setDestination(self.LWRP_OutputChannel, self.LWRP_Sources[sourceNum]['LWMulticastNumber'])

        else:
            # Invalid address
            self.setErrorMessage("Cannot change destination - Invalid source number specified for button #" + str(sourceNum))
    
    def setErrorMessage(self, message = None, mode = "replace"):
        # Error Message Label
        
        if self.errorLabel is None:
            if message == None:
                message = "No errors reported..."
            
            self.errorLabel = tk.Label(
                self,
                text = message,
                font = ("Arial", 8, "italic"),
                wraplength = 400
            )
            self.errorLabel.pack()
            self.errorLabel.grid(
                column = 0,
                columnspan = self.columnNums,
                row = 100,
                sticky = ("N", "S", "E", "W"),
                padx = 50,
                pady = 5
            )

        elif mode == "replace":
            self.errorLabel.config(text = message)
        elif mode == "append":
            self.errorLabel.config(text = self.errorLabel.cget("text") + "\r\n" + message)

    def about(self):
        variable = tkMessageBox.showinfo('Livewire Simple Delegation Switcher', 'Livewire Simple Delegation Switcher\nCreated by Anthony Eden (http://mediarealm.com.au/)\nVersion: ' + __version__)

    def close(self):
        # Terminate the application
        if self.LWRP is not None:
            self.LWRP.stop()
        
        self.root.destroy()

    def updates(self):
        if self.autoCheckVersion is False:
            # Send a check for new updates
            self.versionCheck("popup")

        elif self.newVersion is True:
            variable = tkMessageBox.showinfo('Software Updates', 'You currently have version v' + __version__ + '\r\nVersion v' + self.newVersionNum + ' is available\r\nDownload website: ' + self.newVersionURL)
        else:
            variable = tkMessageBox.showinfo('Software Updates', 'You currently have the latest version v ' + __version__)

    def versionCheck(self, mode = "toolbar"):
        # This simple version checker will prompt the user to update if required
        r_data = {
            'version': __version__,
            'product': __product__
        }

        try:
            r_version = requests.post("http://api.mediarealm.com.au/versioncheck/", data = r_data)
            r_version_response = r_version.json()

            self.autoCheckVersion = True

            if r_version_response['status'] == "update-available" and mode == "toolbar":
                self.setErrorMessage(r_version_response['message'], "append")
                self.newVersion = True
                self.newVersionNum = r_version_response['version_latest']
                self.newVersionText = r_version_response['message']
                self.newVersionURL = r_version_response['url_download']

            elif r_version_response['status'] == "update-available" and mode == "popup":
                self.newVersion = True
                self.newVersionNum = r_version_response['version_latest']
                self.newVersionText = r_version_response['message']
                self.newVersionURL = r_version_response['url_download']
                self.updates()
            
            elif mode == "popup":
                self.newVersion = False
                self.updates()
            
            else:
                self.newVersion = False
            
        except Exception, e:
            print "ERROR Checking for Updates:", e


if __name__ == "__main__":
    app = Application()
    app.master.title('Livewire Simple Delegation Switcher')
    app.mainloop()
