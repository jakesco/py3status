#!/usr/bin/python3


import json
import signal
import subprocess
import sys
import threading
from dataclasses import KW_ONLY, dataclass, field
from datetime import datetime
from functools import partial
from typing import Any, Callable

import psutil

# All blocks will still refresh every 5 mins if no timer is set
MAX_REFRESH_TIME = 300
printf = partial(print, flush=True)


@dataclass
class Header:
    version: int = 1
    click_events: bool = False
    cont_signal: int = signal.SIGCONT
    stop_signal: int = signal.SIGSTOP

    def serialize(self) -> str:
        return json.dumps(vars(self))

    def print_prelude(self) -> None:
        printf(self.serialize())
        printf("[")


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
    separator: bool | None = True
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
        output = [block.info.to_dict() for block in self.line]
        printf(f"{json.dumps(output)}")
        while self.running:
            self.event.wait(timeout=MAX_REFRESH_TIME)
            output = [block.info.to_dict() for block in self.line]
            printf(f",{json.dumps(output)}")
            self.event.clear()
        printf("]")

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

def shell(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

"""
Define blocks here.
"""


def time_block(block: BlockInfo) -> None:
    block.full_text = datetime.now().strftime(" %a %b %d %_I:%M %p ")


def volume_block(block: BlockInfo) -> None:
    result = shell(["wpctl", "get-volume", "@DEFAULT_SINK@"])
    if "[MUTED]" in result:
        block.full_text = "󰕾 mute "
        block.color = "#777777"
    else:
        vol = float(result.split()[1]) * 100
        block.full_text = f"󰕾 {vol:.0f}% "
        block.color = None


def battery_block(block: BlockInfo) -> None:
    block.color = None
    battery = psutil.sensors_battery()

    if battery.power_plugged:
        block.color = "#40a02b"

    icon = " "
    if 60 < battery.percent <= 80:
        icon = " "
    elif 40 < battery.percent <= 60:
        icon = " "
    elif 10 < battery.percent <= 40:
        icon = " "
    else:
        icon = " "
        block.color = "#d20f39"

    block.full_text = f" {icon}{battery.percent:.0f}% "


# Run with /path/to/py3status.py
# Trigger with pkill -RTMIN+x py3status
# TODO: don't use psutil
blocks = [
    # Block(volume_block, signal=signal.SIGRTMIN),
    Block(battery_block, timer=60),
    Block(time_block, timer=1),
]

sys.exit(main(blocks))
