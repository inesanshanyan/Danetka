from typing import Literal
from pydantic import BaseModel, Field

class GameAnswer(BaseModel):
    """
    Structured response for Danetka LLM answers.
    """
    answer: Literal[
        "yes",
        "no",
        "you won! game over",
        "please ask only yes/no questions"
    ] = Field(..., description="The type of answer from the host")

    solution: str | None = Field(
        None,
        description="If the solution is revealed, put the solution text here."
    )
    hint: str | None = Field(
        None,
        description="If a hint is provided, include it here."
    )
    hint_count: int | None = Field(
        None,
        description="Number of hints already given (0-3)."
    )
