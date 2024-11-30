from enum import StrEnum


class EnumImageStatus(StrEnum):
    completed = "completed"
    in_progress = "in_progress"
    error = "error"
    created = "created"
