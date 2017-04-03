#!/usr/bin/python3

import sys
import socket

class PyBot:
  
  #PyBot object constructor 
  def __init__(self,host,port,channel,secret):

    self.host = host
    self.port = port
    self.channel = channel
    self.secret = secret
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,int(port)))
    user = 'AndrewBot'
    try:
      s.send(bytes("NICK "+user+"\n","UTF-8"))
      s.send(bytes("USER "+user+" "+user+" "+user+" "+user+"\n","UTF-8"))
      print("DEUBG --> Successfully joined IRC server "+ host)
    except:
      print("DEBUG -> unable to join server")
    while True:
      #Join the Channel
      s.send(bytes("JOIN "+channel+"\n","UTF-8"))
      data = ""
      while data.find("End of /NAMES list.") == -1:
        data = s.recv(4096).decode("UTF-8")
        data = data.strip('\n\r')
      print("DEUBG -> Successfully joined " + channel)
    
  #function: changeChannel( arg1: new channel )
  #description: quits current channel and joins another specified channel
  def changeChannel(self,newChannel):
    print("Changing channel")     

  def getChannel(self):
    return self.channel
  
#Main
if __name__ == '__main__':

  if(len(sys.argv) == 5):
    host = sys.argv[1]
    port = sys.argv[2]
    channel = "#"+sys.argv[3]
    secret = sys.argv[4]
    bot = PyBot(host,port,channel,secret)
  else:
    print("Incorrect number of arguments")
    sys.exit("Usage: bot <hostname> <port> <channel> <secret-phrase>")
  bot = PyBot(host,port,channel,secret)
  #bot.changeChannel("#godlovesusall")
