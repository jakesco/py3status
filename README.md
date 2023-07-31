# py3status

A program for generating a statusbar for sway and i3 window managers.

## Requirements

- python >= 3.10
- psutil

## Installation

Simply copy `py3status.py` onto your path and run via your sway `status_command`.

## Signals

Blocks can be updated immediately by sending the corresponding **signal** to the `py3status` process.
You can signal a block with `pkill -RTMIN+<x> py3status` where `x` is the assigned **signal** minus 34.
For example, `pkill -RTMIN+1 py3status` will update the block with **signal** 35.

> Note if multiple blocks are assigned the same **signal** assigned only the first will be updated.

## Usage

TODO
