# py3status
A program for generating a statusbar for sway and i3 window managers.

Blocks can be updated immediately by sending the corresponding **updateSignal** to the py3status process.
For example, `kill -35 $(pidof py3status)` will update the block with **updateSignal** 35.
Alternatively, you can signal a block with `pkill -RTMIN+<x> py3status` where `x` is the **updateSignal** minus 34.
So `pkill -RTMIN+1 py3status` will update blocks with **updateSignal** 35.

> Note if multiple blocks are assigned the same **updateSignal** only the first will be updated.

TODO: psutil
