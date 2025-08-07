from enum import StrEnum

class TaskType(StrEnum):
    ROUTINE = "routine"
    FOCUS = "focus"
    CHALLENGE = "challenge"

class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
