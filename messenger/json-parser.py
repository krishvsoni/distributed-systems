#!/usr/bin/env python3
import sys
import json

def main():
	# Read JSON messages from stdin, one per line
	for line in sys.stdin:
		line=line.strip()
		if not line:
			continue
		try:
			msg=json.loads(line)
			src=msg.get("src", "unknown")
			dest=msg.get("dest", "unknown")
			body=msg.get("body", {})
			body_type=body.get("type", "unknown")
			print(f"PARSED: {src}|{dest}|{body_type}")
			print(f"DEBUG: src={src}, dest={dest}, body={body}", file=sys.stderr)
		except Exception as e:
			print(f"ERROR: Failed to parse line: {line}", file=sys.stderr)
			print(f"ERROR: {e}", file=sys.stderr)
		

if __name__ == "__main__":
	main()
