#!/usr/bin/env python3
import sys
import json

class Node:
    def __init__(self):
        self.node_id = None
        self.node_ids = []
        self.next_msg_id = 0
    
    def send(self, dest, body):
        #  Implementing message sending
        msg={
            "src":self.node_id,
            "dest":dest,
            "body":body
        }
        print(json.dumps(msg))
        sys.stdout.flush() 

        
    
    def reply(self, request, body):
        # Implement reply with in_reply_to
        body["in_reply_to"] = request["body"]["msg_id"]
        body["msg_id"] = self.next_msg_id
        self.next_msg_id = self.next_msg_id + 1
        self.send(request["src"],body)
        



def main():
    node = Node()
    
    for line in sys.stdin:
        message = json.loads(line)
        body = message["body"]
        msg_type = body["type"]
        
        if msg_type == "init":
            #  Handle init message
            # 1. Store node_id and node_ids
            # 2. Reply with init_ok
            node.node_id = body["node_id"]
            node.node_ids = body["node_ids"]
            response_body ={
                "type":"init_ok"  #acknowledgement in network protocol
            }
            node.reply(message, response_body)
        else:
            #  Handle other message types (e.g., echo, broadcast, read, topology)
            print(f"Received message of type {msg_type} from {message['src']}", file=sys.stderr)
            # For now, just log the message. You can implement specific logic for each type as needed.
            
if __name__ == "__main__":
    main()



