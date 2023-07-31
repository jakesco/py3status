#!/usr/bin/python3
from __future__ import annotations

import json
import signal
import sys
import threading
from dataclasses import KW_ONLY, dataclass, field
from datetime import datetime
from typing import Any, Callable

# All blocks will still refresh every 5 mins if no timer is set
MAX_REFRESH_TIME = 300


@dataclass
class Header:
    version: int = 1
    click_events: bool = False
    cont_signal: int = signal.SIGCONT
    stop_signal: int = signal.SIGSTOP

    def serialize(self) -> str:
        return json.dumps(vars(self))

    def print_prelude(self) -> None:
        print(self.serialize())
        print("[")
        print("[]")


@dataclass
class BlockInfo:
    full_text: str = ""
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
class Block:
    updater: Callable[[BlockInfo], None]
    _: KW_ONLY
    signal: int | None = None
    timer: int = MAX_REFRESH_TIME
    info: BlockInfo = field(default_factory=BlockInfo)

    def __post_init__(self):
        event = threading.Event()
        if self.signal is not None:
            signal.signal(self.signal, lambda s, h: event.set())
        self.event = event

    def run(self, sigbar: threading.Event) -> None:
        self.updater(self.info)
        while True:
            self.event.wait(timeout=self.timer)
            self.updater(self.info)
            sigbar.set()
            self.event.clear()


@dataclass
class StatusLine:
    line: list[Block]
    event: threading.Event = field(default_factory=threading.Event)
    running: bool = True

    def __post_init__(self):
        signal.signal(signal.SIGINT, lambda s, h: self.stop())

    def run(self):
        while self.running:
            self.event.wait(timeout=MAX_REFRESH_TIME)
            output = [block.info.to_dict() for block in self.line]
            print(f",{json.dumps(output)}")
            self.event.clear()
        print("]")

    def stop(self):
        self.running = False
        self.event.set()


def main(blocks: list[Block]) -> int:
    # Any signal can be handled but RTMIN - RTMAX are best supported
    # TODO: Confirm this 34 - 42
    status_line = StatusLine(blocks)

    sl_thread = threading.Thread(target=status_line.run)
    block_threads = [
        threading.Thread(target=block.run, args=(status_line.event,), daemon=True)
        for block in blocks
    ]

    Header().print_prelude()

    sl_thread.start()
    for thread in block_threads:
        thread.start()

    sl_thread.join()
    return 0


"""
Define blocks here.
"""


def date_block_updater(block: BlockInfo) -> None:
    block.full_text = datetime.now().strftime("%a %b %d %_I:%M %p")


def test_block_updater(block: BlockInfo) -> None:
    if block.full_text == "":
        block.full_text = str(1)
    n = int(block.full_text)
    block.full_text = str(n + 1)


if __name__ == "__main__":
    # Run with /path/to/py3status.py
    # Trigger with pkill -RTMIN+x py3status
    blocks = [
        Block(date_block_updater, timer=1),
        Block(test_block_updater, signal=signal.SIGRTMIN),
        Block(test_block_updater, timer=10, signal=signal.SIGRTMIN+1),
    ]

    sys.exit(main(blocks))