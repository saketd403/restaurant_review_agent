from pydantic import BaseModel, Field, ConfigDict, model_validator, ValidationError
from typing import Optional

class Route(BaseModel):

    can_answer: bool = Field(
        description="""
        True if the model has enough context to answer;
        False if information is missing or ambiguous.
        """
    )

    answer: Optional[str] = Field(
        description="""
        Complete response to the user’s question. Present ONLY 
        when can_answer is True.
        """,
        default=None
    )

    reason: str = Field(
        description="""
        Brief explanation/reasoning of why this query could or could not 
        be fully answered using only the information provided. 
        """
    )

    model_config = ConfigDict(extra='forbid',strict=True)

    @model_validator(mode="after")
    def _exclusive_fields(cls,self):

        if self.can_answer:
            if not self.answer:
                raise ValueError("`answer` must be provided when `can_answer` is True.")
        else:  
            if self.answer is not None:
                raise ValueError(
                    "`answer` must be omitted when `can_answer` is False."
                )
        return self
    
class Filter(BaseModel):

    is_relevant: bool = Field(
        description="""
        True if the review can be used to answer the user query;
        False if the review is irrelevant.
        """
    )
    reasoning : str = Field(
        description="""
        Explanation for your decision.
        """
    )
    model_config = ConfigDict(extra='forbid')

class Rank(BaseModel):

    score : int = Field(
        description="""
        Relevance score for given review. Must be greater than or equal to 1 and less than or equal to 10.
        """
    )

    reasoning : str = Field(
        description="""
        Rationale behind your scoring.
        """
    )

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode="after")
    def _range_fields(cls,self):

        if self.score<1 or self.score>10:
            
            raise ValueError("Score must be between 1 and 10.")

        return self

class Consolidate(BaseModel):

    answer : str