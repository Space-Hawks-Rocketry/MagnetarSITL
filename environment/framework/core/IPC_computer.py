import zmq
import json

class IPC_Computer:
  
  def __init__(self):
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.REQ)
    
  def start(self, port: int):
    self.socket.connect("tcp://localhost:" + str(port))
    
  def close(self):
    self.socket.close()
    self.context.destroy()
    
  def recvJSON(self):
    msg_string = self.socket.recv_string()
    return json.loads(msg_string)
  
  def sendJSON(self, msg_json):
    msg_string = json.dumps(msg_json)
    self.socket.send_string(msg_string)
    