from enum import Enum
import logging

class ExecutionType(Enum):
    TEST = 1
    PRODUCTION = 2


EXECUTION_TYPE_TO_LOGGER_LEVEL = {
    ExecutionType.TEST : logging.DEBUG,
    ExecutionType.PRODUCTION : logging.INFO,
    }