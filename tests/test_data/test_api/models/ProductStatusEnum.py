from enum import Enum


class ProductStatusEnum(str, Enum):

    NEW = "new"
    ERROR = "error"
    COMPLETED = "completed"
