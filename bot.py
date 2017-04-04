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
    self.controlMode = 0 #default 0 = bot not being controller

    try:
      self.s = s.connect((host,int(port)))
      s.send(bytes("NICK " + self.nick + "\n", "UTF-8"))
      s.send(bytes("USER " +self.nick+" "+self.nick+" "+self.nick+ " " + self.nick+ "\n","UTF-8"))
    except:
      print("unable to connect to irc server")
    s.send(bytes("JOIN " + channel + "\n", "UTF-8")) #Join channel

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
    if message == secret:
      print("DEBUG --> Controller said the secret! Control Mode enabled, read to troll and annoy")
      self.control = 1

  def changeChannel(self,newChannel):
    print("DEBUG --> Changing channel")     

  def generateRandomName(self):
    randomName = "Andrew" + random.choice(string.digits)
    randomName += random.choice(string.digits)
    randomName += random.choice(string.digits)
    randomName += random.choice(string.digits)
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
  












