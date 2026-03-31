#!/usr/bin/env python3
import sys
import json
import threading


class Node:
    def __init__(self):
        self.node_id = None
        self.node_ids = []
        self.next_msg_id = 0
        self.sequence = 0
        self.lock = threading.Lock()

    def send(self, dest, body):
        body["msg_id"] = self.next_msg_id
        self.next_msg_id += 1

        message = {
            "src": self.node_id,
            "dest": dest,
            "body": body
        }

        print(json.dumps(message), flush=True)

    def reply(self, request, body):
        body["in_reply_to"] = request["body"]["msg_id"]
        self.send(request["src"], body)

    def generate_id(self):
        # Simple deterministic ID (what test expects)
        with self.lock:
            unique_id = f"{self.node_id}-{self.sequence}"
            self.sequence += 1
            return unique_id


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

        elif msg_type == "generate":
            unique_id = node.generate_id()
            node.reply(message, {
                "type": "generate_ok",
                "id": unique_id
            })


if __name__ == "__main__":
    main()