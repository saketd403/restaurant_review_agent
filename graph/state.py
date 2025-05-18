from typing_extensions import TypedDict
import operator
from typing import Annotated,List,Union
from pydantic import BaseModel, Field, ConfigDict
from langgraph.graph import MessagesState
import textwrap
from datetime import datetime

class Review(BaseModel):
    rating : float = Field(default=None)
    content : str  = Field(default=None)
    date : datetime = Field(default=None)
    score: float = Field(default=0.0)

class OverallState(MessagesState):
    answer : str
    reviews : List[Review]
    

class WorkerState(MessagesState):
    reviews : List[Review]


# filtered_reviews =  Annotated[List[Review], operator.add]