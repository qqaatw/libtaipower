import os

TEST_ACCOUNT = os.environ["TEST_ACCOUNT"] if "TEST_ACCOUNT" in os.environ else None
TEST_PASSWORD = os.environ["TEST_PASSWORD"] if "TEST_PASSWORD" in os.environ else None
TEST_ELECTRIC_NUMBER = os.environ["TEST_ELECTRIC_NUMBER"] if "TEST_ELECTRIC_NUMBER" in os.environ else None

MOCK_ELECTRIC_NUMBER = "00123456700"