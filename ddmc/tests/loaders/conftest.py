import os

os.environ["TESTCONTAINERS_RYUK_DISABLED"] = (
    "true"  # prevent ryuk container from testcontainers
)
