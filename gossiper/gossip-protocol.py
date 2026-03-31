#!/usr/bin/env python3
import sys
import json
import random

# TODO: Implement gossip with random neighbor selection

class Node:
    def  __init__(self):
        self.node_id = None
        self.node_ids = []
        self.next_msg_id = 0
        self.neighbors = []
        self.messages = set()

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