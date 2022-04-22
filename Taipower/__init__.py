__author__ = "Allan Lin"
__version__ = "0.0.3"

import asyncio
import sys


if sys.platform == "win32": # https://stackoverflow.com/questions/61543406/asyncio-run-runtimeerror-event-loop-is-closed
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())