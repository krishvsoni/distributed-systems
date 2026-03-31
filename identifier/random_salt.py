#!/usr/bin/env python3
import sys
import json
import time


class Node:
    def __init__(self):
        self.node_id = None
        self.node_ids = []

        # For outgoing messages
        self.next_msg_id = 0

        # For unique ID generation
        self.last_timestamp = 0
        self.sequence = 0

    def send(self, dest, body):
        # Assign unique msg_id for every outgoing message
        body["msg_id"] = self.next_msg_id
        self.next_msg_id += 1

        message = {
            "src": self.node_id,
            "dest": dest,
            "body": body
        }

        # Send message to stdout (this is your "network")
        print(json.dumps(message), flush=True)

    def reply(self, request, body):
        # Attach correlation ID so requester knows which request this is for
        body["in_reply_to"] = request["body"]["msg_id"]

        # Send response back to original sender
        self.send(request["src"], body)

    def generate_id(self):
        # Generate timestamp in milliseconds
        timestamp = int(time.time() * 1000)

        # Handle clock going backwards (important edge case)
        if timestamp < self.last_timestamp:
            timestamp = self.last_timestamp

        # If multiple IDs generated in same millisecond → increment sequence
        if timestamp == self.last_timestamp:
            self.sequence += 1
        else:
            self.sequence = 0
            self.last_timestamp = timestamp

        # Final ID structure:
        # node_id + timestamp + sequence ensures uniqueness
        return f"{self.node_id}-{timestamp}-{self.sequence}"


def main():
    node = Node()

    for line in sys.stdin:
        message = json.loads(line)
        body = message["body"]
        msg_type = body["type"]

        if msg_type == "init":
            # Store node identity and cluster info
            node.node_id = body["node_id"]
            node.node_ids = body["node_ids"]

            # Respond with init_ok
            node.reply(message, {"type": "init_ok"})

        elif msg_type == "generate":
            # Generate unique ID
            unique_id = node.generate_id()

            # Send response back
            node.reply(message, {
                "type": "generate_ok",
                "id": unique_id
            })


if __name__ == "__main__":
    main()