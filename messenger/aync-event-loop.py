#!/usr/bin/env python3
import sys
import json
import threading
from queue import Queue

class Node:
    def __init__(self):
        self.node_id = None
        self.node_ids = []
        self.next_msg_id = 0
        self.lock = threading.Lock()

        self.output_buffer = []
        self.buffer_lock = threading.Lock()
    
    def send(self, dest, body):
        with self.lock:
            msg_id = self.next_msg_id
            self.next_msg_id += 1
            
        body["msg_id"] = msg_id
        message = {"src": self.node_id, "dest": dest, "body": body}
        
        with self.buffer_lock:
            self.output_buffer.append(message)
    
    def reply(self, request, body):
        body["in_reply_to"] = request["body"].get("msg_id")
        self.send(request["src"], body)
    
    def handle_message(self, message):
        body = message.get("body", {})
        typ = body.get("type")

        if typ == "init":
            self.node_id = body.get("node_id")
            self.node_ids = body.get("node_ids")
            self.reply(message, {"type": "init_ok"})
        elif typ == "echo":
            self.reply(message, {"type": "echo_ok", "echo": body.get("echo")})

    def flush_output(self):
        with self.buffer_lock:
            self.output_buffer.sort(key=lambda m: m["body"].get("in_reply_to", -1))
            for msg in self.output_buffer:
                print(json.dumps(msg), flush=True)

def worker(node, q):
    while True: 
        msg = q.get()
        if msg is None:
            q.task_done()
            break

        try:
            node.handle_message(msg)
        finally:
            q.task_done()

def main():
    node = Node()
    q = Queue()
    
    # 1. Handle "init" synchronously
    input_stream = sys.stdin
    for line in input_stream:
        if not line.strip(): continue
        msg = json.loads(line)
        
        if msg["body"]["type"] == "init":
            node.handle_message(msg)
            break # Stop sync processing once initialized
    
    # 2. Spawn worker threads for subsequent messages
    workers = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(node, q))
        t.start()
        workers.append(t)

    # 3. Read remaining messages into the queue
    for line in input_stream:
        if not line.strip(): continue
        q.put(json.loads(line))

    # 4. Cleanup and Flush
    for _ in range(len(workers)):
        q.put(None)
    q.join()
    for t in workers:
        t.join()

    # 5. Final deterministic output
    node.flush_output()

if __name__ == "__main__":
    main()