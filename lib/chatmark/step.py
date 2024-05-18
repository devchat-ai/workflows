import time
from contextlib import AbstractContextManager

from lib.ide_service import IDEService


class Step(AbstractContextManager):
    """
    Show a running step in the TUI.

    ChatMark syntax:

    ```Step
    # Something is running...
    some details...
    ```

    Usage:
    with Step("Something is running..."):
        print("some details...")
    """

    def __init__(self, title: str):
        self.title = title
        self.enter_time = time.time()

    def __enter__(self):
        print(f"\n```Step\n# {self.title}", flush=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # close the step
        end_time = time.time()
        IDEService().ide_logging(
            "debug", f"Step {self.title} took {end_time - self.enter_time:.2f} seconds"
        )
        print("\n```", flush=True)
