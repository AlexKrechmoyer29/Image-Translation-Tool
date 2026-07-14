"""Small Qt helpers shared by the test modules."""

import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication


def get_application():
    """Return the process-wide QApplication required by widget tests."""
    application = QApplication.instance()
    if application is None:
        application = QApplication([])
    return application


def wait_for(predicate, timeout=3.0):
    """Process Qt events until predicate is true or the timeout expires."""
    application = get_application()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        application.processEvents()
        if predicate():
            return True
        time.sleep(0.01)
    application.processEvents()
    return predicate()
