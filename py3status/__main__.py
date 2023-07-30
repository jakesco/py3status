import json
import signal
import subprocess
import sys
from dataclasses import dataclass
from time import sleep
from typing import Any

from concurrent.futures import ThreadPoolExecutor


@dataclass
class Header:
    version: int = 1
    click_events: bool = False
    cont_signal: int = signal.SIGCONT
    stop_signal: int = signal.SIGSTOP

    def dumps(self) -> str:
        return json.dumps(self.__dict__)


@dataclass
class Block:
    full_text: str
    short_text: str | None = None
    color: str | None = None
    background: str | None = None
    border: str | None = None
    border_top: int | None = None
    border_bottom: int | None = None
    border_left: int | None = None
    border_right: int | None = None
    min_width: int | None = None
    align: str | None = None
    name: str | None = None
    instance: str | None = None
    urgent: bool | None = None
    separator: bool | None = None
    separator_block_width: int | None = None
    markup: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in vars(self).items() if v is not None}

@dataclass
class Process:
    command: str
    block: Block
    timer: int = 1
    signal: int | None = None

    def run(self) -> None:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        self.block.full_text = result.stdout.strip()


@dataclass
class StatusLine:
    blocks: dict[int, Process]

    def dumps(self) -> str:
        return json.dumps([process.block.to_dict() for _, process in self.blocks.items()])


command = "date +'%a %b %d %_I:%M:%s %p'"


def handler(signum, handler):
    print("exiting early", file=sys.stderr)
    print("]")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    header = Header()
    block1 = Block("")
    line = StatusLine({1: Process(command, block1)})
    print(header.dumps(), flush=True)
    print("[", flush=True)
    print("[]", flush=True)
    for _ in range(10):
        for _, p in line.blocks.items():
            p.run()
        output = line.dumps()
        print(f",{output}", flush=True)
        sleep(1)
    print("]")
    sys.exit(0)
