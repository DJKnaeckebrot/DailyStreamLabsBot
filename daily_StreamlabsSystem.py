#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Daily command"""
#---------------------------------------
# Libraries and references
#---------------------------------------
import codecs
import json
import os
import winsound
import ctypes
from array import *
#---------------------------------------
# [Required] Script information
#---------------------------------------
ScriptName = "Daily"
Website = "https://github.com/mrdennis1212"
Creator = "mrdennis1212"
Version = "1.0.1"
Description = "Daily command"
#---------------------------------------
# Versions
#---------------------------------------
""" Releases (open README.md for full release notes)
1.0 - Initial Release
"""
#---------------------------------------
# Variables
#---------------------------------------
settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")

#---------------------------------------
# Classes
#---------------------------------------
class Settings:
    """" Loads settings from file if file is found if not uses default values"""

    # The 'default' variable names need to match UI_Config
    def __init__(self, settingsFile=None):
        if settingsFile and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')

        else: #set variables if no custom settings file is found
            self.OnlyLive = False
            self.Command = "!daily"
            self.Cost = 0
            self.Permission = "Everyone"
            self.PermissionInfo = ""
            self.Usage = "Stream Chat"
            self.UseCD = True            
            self.UserCooldown = 86400
            self.OnUserCooldown = "{0} the command is still on user cooldown for {1} hours!"
            self.OnUserCooldownMinute = "{0} the command is still on user cooldown for {1} minutes!"
            self.ResponseMessage = "{0} ich schenke dir {1} {2}! Du hast also {3} {2}!"
            self.CasterCD = True
            self.Timeout = False
            self.TL = 60
            self.DailyRewards = 200

    # Reload settings on save through UI
    def ReloadSettings(self, data):
        """Reload settings on save through UI"""
        self.__dict__ = json.loads(data, encoding='utf-8-sig')
        return

    # Save settings to files (json and js)
    def SaveSettings(self, settingsFile):
        """Save settings to files (json and js)"""
        with codecs.open(settingsFile, encoding='utf-8-sig', mode='w+') as f:
            json.dump(self.__dict__, f, encoding='utf-8-sig')
        with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig', mode='w+') as f:
            f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8-sig', ensure_ascii=False)))
        return
#---------------------------------------
# [OPTIONAL] Settings functions
#---------------------------------------
def SetDefaults():
    """Set default settings function"""

    #play windows sound
    winsound.MessageBeep()

    #open messagebox with a security check
    MessageBox = ctypes.windll.user32.MessageBoxW
    returnValue = MessageBox(0, u"You are about to reset the settings, "
                                "are you sure you want to contine?"
                             , u"Reset settings file?", 4)

    #if user press "yes"
    if returnValue == 6:

        # Save defaults back to file
        Settings.SaveSettings(MySet, settingsFile)

        #show messagebox that it was complete
        MessageBox = ctypes.windll.user32.MessageBoxW
        returnValue = MessageBox(0, u"Settings successfully restored to default values"
                                 , u"Reset complete!", 0)

#---------------------------------------
# [Required] functions
#---------------------------------------
def Init():
    """data on Load, required function"""
    global MySet
    MySet = Settings(settingsFile)

def Execute(data):
    """Required Execute data function"""
    if data.IsChatMessage() and data.GetParam(0).lower() == MySet.Command.lower():

        # check if source is valid
        if not IsFromValidSource(data, MySet.Usage):
            return

        # check is permissions are ok
        if not Parent.HasPermission(data.User, MySet.Permission, MySet.PermissionInfo):
            message = MySet.PermissionResponse.format(data.User, MySet.Permission, MySet.PermissionInfo)
            SendResp(data, message)

        if not HasPermission(data):
            return

        # check for onlylive setting or if user is online
        if not MySet.OnlyLive or Parent.IsLive():

            # reject on cooldown
            if IsOnCooldown(data):
                return

            # Add daily rewards to user account             
            Parent.AddPoints(data.User, data.UserName, MySet.DailyRewards)

            # output user balance
            userBalance = str(Parent.GetPoints(data.User))
            message = MySet.ResponseMessage.format(data.UserName, str(MySet.DailyRewards), Parent.GetCurrencyName(), userBalance)

            SendResp(data, message)

            AddCooldown(data)
            

def Tick():
    """Required tick function"""

#---------------------------------------
# [Optional] Functions for usage handling
#---------------------------------------
def SendResp(data, sendMessage):
    """Sends message to Stream or discord chat depending on settings"""

    if not data.IsFromDiscord() and not data.IsWhisper():
        Parent.SendStreamMessage(sendMessage)

    if not data.IsFromDiscord() and data.IsWhisper():
        Parent.SendStreamWhisper(data.User, sendMessage)

    if data.IsFromDiscord() and not data.IsWhisper():
        Parent.SendDiscordMessage(sendMessage)

    if data.IsFromDiscord() and data.IsWhisper():
        Parent.SendDiscordDM(data.User, sendMessage)

def CheckUsage(data, rUsage):
    """Return true or false depending on the message is sent from
    a source that's in the usage setting or not"""

    if not data.IsFromDiscord():
        l = ["Stream Chat", "Chat Both", "All", "Stream Both"]
        if not data.IsWhisper() and (rUsage in l):
            return True

        l = ["Stream Whisper", "Whisper Both", "All", "Stream Both"]
        if data.IsWhisper() and (rUsage in l):
            return True

    if data.IsFromDiscord():
        l = ["Discord Chat", "Chat Both", "All", "Discord Both"]
        if not data.IsWhisper() and (rUsage in l):
            return True

        l = ["Discord Whisper", "Whisper Both", "All", "Discord Both"]
        if data.IsWhisper() and (rUsage in l):
            return True

    return False

def IsOnCooldown(data):
    """Return true if command is on cooldown and send cooldown message if enabled"""
    userCooldown = Parent.IsOnUserCooldown(ScriptName, MySet.Command, data.User)
    caster = (Parent.HasPermission(data.User, "Caster", "") and MySet.CasterCD)

    if userCooldown and caster is False:

        if MySet.UseCD:
            userCDD = Parent.GetUserCooldownDuration(ScriptName, MySet.Command, data.User)

            if userCDD < 3600:
                m_CooldownRemaining = userCDD/60

                message = MySet.OnUserCooldownMinute.format(data.UserName, m_CooldownRemaining)
                SendResp(data, message)

            else:
                m_CooldownRemaining = userCDD/3600

                message = MySet.OnUserCooldown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, message)
        return True
    return False

def HasPermission(data):
    """Returns true if user has permission and false if user doesn't"""
    if not Parent.HasPermission(data.User, MySet.Permission, MySet.PermissionInfo):
        message = MySet.PermissionResponse.format(data.UserName, MySet.Permission, MySet.PermissionInfo)
        SendResp(data, message)
        return False
    return True

def IsFromValidSource(data, Usage):
    """Return true or false depending on the message is sent from
    a source that's in the usage setting or not"""
    if not data.IsFromDiscord():
        l = ["Stream Chat", "Chat Both", "All", "Stream Both"]
        if not data.IsWhisper() and (Usage in l):
            return True

        l = ["Stream Whisper", "Whisper Both", "All", "Stream Both"]
        if data.IsWhisper() and (Usage in l):
            return True

    if data.IsFromDiscord():
        l = ["Discord Chat", "Chat Both", "All", "Discord Both"]
        if not data.IsWhisper() and (Usage in l):
            return True

        l = ["Discord Whisper", "Whisper Both", "All", "Discord Both"]
        if data.IsWhisper() and (Usage in l):
            return True
    return False

def AddCooldown(data):
    """add cooldowns"""
    if Parent.HasPermission(data.User, "Caster", "") and MySet.CasterCD:
        Parent.AddCooldown(ScriptName, MySet.Command, MySet.UserCooldown)
        return

    else:
        Parent.AddUserCooldown(ScriptName, MySet.Command, data.User, MySet.UserCooldown)
        # Parent.AddCooldown(ScriptName, MySet.Command, MySet.Cooldown)
