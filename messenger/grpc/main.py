import grpc
from concurrent import futures
import json
import sys
import time
import threading

import message_pb2
import message_pb2_grpc



class MessageService(message_pb2_grpc.MessageServiceServicer):

    def ProcessMessage(self, request, context):
        try:
            # Parse JSON body
            body = json.loads(request.body)

            src = request.src or "unknown"
            dest = request.dest or "unknown"
            body_type = body.get("type", "unknown")

            parsed = f"{src}|{dest}|{body_type}"

            # stdout (data)
            print(f"PARSED: {parsed}")

            # stderr (logs)
            print(
                f"DEBUG: src={src}, dest={dest}, body={body}",
                file=sys.stderr
            )

            return message_pb2.MessageResponse(
                status="OK",
                parsed=parsed
            )

        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)

            return message_pb2.MessageResponse(
                status="ERROR",
                parsed=str(e)
            )


def start_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    message_pb2_grpc.add_MessageServiceServicer_to_server(
        MessageService(), server
    )

    server.add_insecure_port('[::]:50051')
    server.start()

    print("gRPC server running on port 50051")

    return server


def run_client():
    channel = grpc.insecure_channel('localhost:50051')
    stub = message_pb2_grpc.MessageServiceStub(channel)

    msg = {
        "type": "ping",
        "payload": "hello"
    }

    response = stub.ProcessMessage(
        message_pb2.MessageRequest(
            src="client1",
            dest="server1",
            body=json.dumps(msg)
        )
    )

    print("CLIENT RECEIVED:", response.status, response.parsed)


def run_parallel_clients(n=10):
    threads = []

    for i in range(n):
        t = threading.Thread(target=run_client)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()



if __name__ == "__main__":
    server = start_server()

    # Give server time to start
    time.sleep(1)

    # Single request
    run_client()

    # Uncomment to test concurrency
    # run_parallel_clients(50)

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down...")