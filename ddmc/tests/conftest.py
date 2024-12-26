import pytest


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests",
    )


def pytest_configure(config: pytest.Config):
    config.addinivalue_line("markers", "integration: mark test as integration to run")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]):
    if config.getoption("--integration") or len(items) == 1:
        return  # dont skip if integration flag or speciffic test selected

    skip_integration = pytest.mark.skip(reason="need --integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
