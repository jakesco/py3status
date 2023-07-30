import sys
import json
import signal
import subprocess
from time import sleep

command = "date +'%a %b %d %_I:%M %p'"

def print_output(full_text: str) -> None:
    body = [[{"full_text": full_text}]]
    print(json.dumps(body), flush=True)

def handler(signum, frame):
    print("exiting early", file=sys.stderr)
    print(']')
    sys.exit(0)



if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    header = { "version": 1 }
    print(json.dumps(header), flush=True)
    print('[', flush=True)
    print('[]', flush=True)
    for x in range(5):
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        output = [{"full_text": result.stdout.strip()}]
        print(f",{output}", flush=True)
        sleep(1)
    print(']')
    sys.exit(0)
