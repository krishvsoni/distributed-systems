#!/usr/bin/env python3
import sys
import json

class Node:
    def __init__(self):
        self.node_id = None
        self.node_ids = []
        self.next_msg_id = 0
    
    def send(self, dest, body):
        body["msg_id"] = self.next_msg_id
        self.next_msg_id += 1
        message = {"src": self.node_id, "dest": dest, "body": body}
        print(json.dumps(message), flush=True)
    
    def reply(self, request, body):
        body["in_reply_to"] = request["body"]["msg_id"]
        self.send(request["src"], body)
    
    def validate_message(self, message):
        # Validate message structure
        # Return True if valid, False otherwise
        # Log errors to stderr
        if "src" not in message:
            print("ERROR: Missing 'src' field", file=sys.stderr)
            return False    
        if "dest" not in message:
            print("ERROR: Missing 'dest' field", file=sys.stderr)
            return False
        if "body" not in message:
            print("ERROR: Missing 'body' field", file=sys.stderr)
            return False
            
        body=message["body"]
        if "type" not in body:
            print("ERROR: Missing 'type' field in message body", file=sys.stderr)
            return False
        return True


def main():
    node = Node()
    
    for line in sys.stdin:
        try:
            message = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}", file=sys.stderr)
            continue
        
        # Validate message before processing
        if not node.validate_message(message):
            continue
        else:            print(f"Received valid message: {message}", file=sys.stderr)

        
        body = message["body"]
        msg_type = body["type"]
        
        if msg_type == "init":
            node.node_id = body["node_id"]
            node.node_ids = body["node_ids"]
            node.reply(message, {"type": "init_ok"})
        elif msg_type == "echo":
            node.reply(message, {"type": "echo_ok", "echo": body["echo"]})

if __name__ == "__main__":
    main()
