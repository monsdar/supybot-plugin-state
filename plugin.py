###
# Copyright (c) 2013, Nils Brinkmann
# All rights reserved.
#
#
###

import cPickle
import os

import supybot.callbacks as callbacks
import supybot.conf as conf
import supybot.ircutils as ircutils
import supybot.plugins as plugins
import supybot.utils as utils
from supybot.commands import *

class Subsystem():
    def __init__(self, name, state):
        self.name = name
        self.state = state

class System():
    def __init__(self, name):
        self.name = name
        self.subsystems = []
        
    def output(self, irc):
        irc.reply("\x02 -- " + self.name + " -- \x02")
        
        #check the size of the longest sub
        sizeLongestSub = 0
        for sub in self.subsystems:
            if( len(sub.name) > sizeLongestSub ):
                sizeLongestSub = len(sub.name)
                
        #print the subs
        for sub in self.subsystems:
            if( sub.state.lower() == 'ok' ):
                color = "1,9"
            else:
                color = "1,4"
            output = "\x03" + color + "    \x03| "
            output += sub.name + " | " + sub.state
            irc.reply(output)

class State(callbacks.Plugin):
    """This plugin allows to store the state of components, systems, ..."""
    def __init__(self, irc):
        self.__parent = super(State, self)
        self.__parent.__init__(irc)

        self.systems = []

        #read the announcements from file
        filepath = conf.supybot.directories.data.dirize('State.db')
        if( os.path.exists(filepath) ):
            try:
                self.systems = cPickle.load( open( filepath, "rb" ) )
            except EOFError as error:
                irc.reply("Error when trying to load existing data.")
                irc.reply("Message: " + str(error))
        
    def die(self):
        #Pickle the items to a file
        try:
            filepath = conf.supybot.directories.data.dirize('State.db')
            cPickle.dump( self.systems, open( filepath, "wb" ) )
        except cPickle.PicklingError as error:
            print("More: Error when pickling to file...")
            print(error)
            
    def state(self, irc, msg, args, system):
        """<system>
        
        Displays the state of the given <system>"""
        for currentSystem in self.systems:
            if(currentSystem.name == system):
                currentSystem.output(irc)
                irc.replySuccess()
                return
                
        #if the given system has not been found
        irc.error("Cannot find " + system)        
    state = wrap(state, ['somethingWithoutSpaces'])
            
    def list(self, irc, msg, args):
        """takes no arguments
        
        Lists all the existing systems"""
        if( len(self.systems) == 0):
            irc.reply("No systems configured")
            
        for system in self.systems:
            irc.reply( "\x02" + system.name + "\x02" + " - (" + str( len(system.subsystems) ) + " subsystems)"  )
        irc.replySuccess()
    list = wrap(list)
    
    def add(self, irc, msg, args, system, subsystem, state):
        """<system> <subsystem> <state>
        
        Sets the <subsystem> of <system> to the given <state>. If <system> or <subsystem>
        does not exist it'll be created.
        <status> is positive if named like the following: OK
        <status> is negative in every other case, text will be added as a comment"""
        #check if the system already exists
        for currentSystem in self.systems:
            if(currentSystem.name == system):
                #check if the system already exists
                for currentSub in currentSystem.subsystems:
                    if(currentSub.name == subsystem):
                        currentSub.state = state
                        irc.replySuccess()
                        return
                #subsystem hasn't been found, create a new one
                newSub = Subsystem(subsystem, state)
                currentSystem.subsystems.append(newSub)
                irc.replySuccess()
                return
        
        #systems hasn't been found, create a new one
        newSys = System(system)
        newSub = Subsystem(subsystem, state)
        newSys.subsystems.append(newSub)
        self.systems.append(newSys)
        irc.replySuccess()
        
    add = wrap(add, ['somethingWithoutSpaces', 'somethingWithoutSpaces', 'text'])
    
    def remove(self, irc, msg, args, system):
        """<system>
        
        Removes the given <system> completely"""
        #try to find and remove the given system
        for currentSystem in self.systems:
            if(currentSystem.name == system):
                self.systems.remove(currentSystem)
                irc.replySuccess()
                return
                
        #system hasn't been found
        irc.error("Cannot find " + system)
    remove = wrap(remove, ['somethingWithoutSpaces'])
    
    def removesub(self, irc, msg, args, system, subsystem):
        """<system> <subsystem>
        
        Removes the given <subsystem> from the <system>"""
        #try to find the system
        for currentSystem in self.systems:
            if(currentSystem.name == system):
                #try to find the subsystem
                for currentSub in currentSystem.subsystems:
                    if(currentSub.name == subsystem):
                        currentSystem.subsystems.remove(currentSub)
                        irc.replySuccess()
                        return
        
                #no subsystem has been found
                irc.error("No subsystem " + subsystem + " has been found")
                return
                
        #no system has been found
        irc.error("No system " + system + " has been found")
    removesub = wrap(removesub, ['somethingWithoutSpaces', 'somethingWithoutSpaces'])
    
Class = State


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
