#!/usr/bin/env python3
import sys
import json
import threading

class Node:
    def __init__(self):
        self.node_id = None
        self.node_ids = []
        self.next_msg_id = 0
        self.neighbors = []
        self.messages = set()
        self.lock = threading.Lock()
        self.output_lock = threading.Lock()
    
    def send(self, dest, body):
        with self.lock:
            body["msg_id"] = self.next_msg_id
            self.next_msg_id += 1
        message = {"src": self.node_id, "dest": dest, "body": body}
        with self.output_lock:
            print(json.dumps(message), flush=True)
    
    def reply(self, request, body):
        body["in_reply_to"] = request["body"]["msg_id"]
        self.send(request["src"], body)
    
    def broadcast_to_neighbors(self, value, exclude=None):
        # TODO: Send broadcast to all neighbors except sender
        for neighbor in self.neighbors:
            if neighbor == exclude:
                continue
                self.send(neighbor, {"type": "broadcast", "message": value})
            elif msg_type == "topology":
                self.neighbors = body["topology"].get(self.node_id, [])
                self.reply(message, {"type": "topology_ok"})


            elif msg_type == "broadcast":
                value = body["message"]
                if value not in self.messages:
                    self.messages.add(value)
                    self.broadcast_to_neighbors(value, exclude=message["src"])
                node.reply(message, {"type": "broadcast_ok"})

            elif msg_type == "read":
                node.reply(message, {
                    "type": "read_ok",
                    "messages": list(node.messages)
                })

            if value not in node.messages:
                node.messages.add(value)
                node.broadcast_to_neighbors(value, exclude=message["src"])  


        

def main():
    node = Node()
    
    for line in sys.stdin:
        message = json.loads(line)
        body = message["body"]
        msg_type = body["type"]
        
        if msg_type == "init":
            node.node_id = body["node_id"]
            node.node_ids = body["node_ids"]
            node.reply(message, {"type": "init_ok"})

        elif msg_type == "topology":
            # Store only this node's neighbors
            topology = body["topology"]
            node.neighbors = topology.get(node.node_id, [])

            node.reply(message, {"type": "topology_ok"})

        elif msg_type == "broadcast":
            value = body["message"]

            # Store message only if new (critical to avoid loops)
            if value not in node.messages:
                node.messages.add(value)

                # Propagate to neighbors except sender
                node.broadcast_to_neighbors(value, exclude=message["src"])

            node.reply(message, {"type": "broadcast_ok"})

        elif msg_type == "read":
            # Return all messages seen so far
            node.reply(message, {
                "type": "read_ok",
                "messages": list(node.messages)
            })


if __name__ == "__main__":
    main()