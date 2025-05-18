from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.types import Command, Send 
import math
from typing import Literal
from pydantic import ValidationError
from datetime import datetime, date
import textwrap

from graph.llm import LLM
from graph.state import OverallState, WorkerState
from restaurant import Restaurant
from graph.output_schema import Route, Filter, Rank, Consolidate
from reviews import Reviews
from config.paths import PATHS
from config.prompts import PROMPTS


def route_query(state:OverallState,config:RunnableConfig)-> Command[Literal[END, "distribute_reviews"]]:

    try:

        input_args = config["configurable"]["input_args"]

        sys_prompt=""
        with open(PROMPTS.route/"sys_prompt.txt","r",encoding='utf-8') as file:

            sys_prompt = file.read()

        restaurant_info = Restaurant(input_args["restaurant_id"])
        restaurant_info = str(restaurant_info)

        system_message = sys_prompt.format(details=restaurant_info)
        system_message = SystemMessage(content=system_message)

        llm_call = LLM(input_args,Route)

        try:
            response = llm_call([system_message]+state["messages"])
        except ValidationError as e:
            print(e.json())
            raise

        if(response.can_answer):

            return Command(
                update = {"answer":response.answer},
                goto = END
            )

        else:

            return Command(
                goto="distribute_reviews"
            )
        
    except Exception as e:

        print(f"Something went wrong in route :\n {e}")
        raise

def distribute_reviews(state:OverallState,config:RunnableConfig):

    try:

        input_args = config["configurable"]["input_args"]
        num_workers = input_args["max_workers"]

        review_obj = Reviews(input_args["restaurant_id"])
        reviews = review_obj.get_reviews()

        if (len(reviews)>0) :
            return {"reviews":reviews}
        else:
            return {"answer":"Not enough information to answer your query."}

    except Exception as e:

        print(f"Something went wrong while reading reviews:\n {e}")
        raise

def continue_to_review(state:OverallState,config:RunnableConfig):

    try:

        input_args = config["configurable"]["input_args"]
        num_workers = input_args["max_workers"]
        reviews = state["reviews"]

        if(len(reviews)==0):
            return END

        num_reviews = len(reviews)

        if num_reviews <= num_workers:
            return [ Send("process_review",{"messages":state["messages"],"reviews":[review]}) for review in reviews]

        allocation = math.ceil(num_reviews/num_workers)

        calls = []
        allocated_reviews=[]

        for worker in range(num_workers):

            if(len(reviews)>allocation):
                allocated_reviews = [reviews.pop() for _ in range(allocation)]
            else:
                allocated_reviews = reviews

            calls.append(Send("process_reviews",{"messages":state["messages"],"reviews":allocated_reviews}))

        return calls

    except Exception as e:

        print(f"Something went wrong while calling review workers:\n {e}")
        raise

def process_reviews(state:WorkerState,config:RunnableConfig):
    
    from graph.graph import build_review_subgraph

    review_subgraph = build_review_subgraph()

    response = review_subgraph.invoke({"messages":state["messages"],"reviews":state["reviews"]}, config=config)

    #filtered_reviews = [review for review in response["reviews"] if review.score>0]
        
    #return {"filtered_reviews":filtered_reviews}

def pretty_print_review(reviews):

    reviews_str=""
    for indx, review in enumerate(reviews):
       reviews_str += f"{str(indx+1)}. {textwrap.fill(review.content, width=80,break_long_words=False, replace_whitespace=False)}\n"

    return reviews_str

def consolidate_reviews(state:OverallState,config:RunnableConfig):

    try:

        input_args = config["configurable"]["input_args"]
        top_k = input_args["top_k"]

        filtered_reviews = [review for review in state["reviews"] if review.score>0]

        if not filtered_reviews :
            return {"answer":"Not enough information to answer your query."}
        
        sorted_reviews = sorted(filtered_reviews, reverse=True, key=lambda obj : obj.score)
        sorted_reviews = sorted_reviews[:top_k]

        reviews_str = pretty_print_review(sorted_reviews)

        restaurant_info = Restaurant(input_args["restaurant_id"])
        restaurant_info = str(restaurant_info)

        sys_prompt=""
        with open(PROMPTS.consolidate/"sys_prompt.txt","r",encoding='utf-8') as file:

            sys_prompt = file.read()

        system_message = sys_prompt.format(reviews=reviews_str, details=restaurant_info)
        system_message = SystemMessage(content=system_message)

        llm_call = LLM(input_args,Consolidate)

        try:
            response = llm_call([system_message]+state["messages"])
        except ValidationError as e:
            print(e.json())
            raise

        return {"answer": response.answer}
    
    except Exception as e:

        print(f"Something went wrong during consolidating reviews :\n {e}")
        raise

    

#### Process review subgraph
def filter_reviews(state:WorkerState,config:RunnableConfig):

    try:

        input_args = config["configurable"]["input_args"]

        sys_prompt=""
        with open(PROMPTS.filter/"sys_prompt.txt","r",encoding='utf-8') as file:

            sys_prompt = file.read()

        examples=""
        with open(PROMPTS.filter/"examples.txt","r",encoding='utf-8') as file:

            examples = file.read()

        filtered_reviews = []

        for review in state["reviews"]:

            system_message = sys_prompt.format(review=review,examples=examples)
            system_message = SystemMessage(content=system_message)

            llm_call = LLM(input_args,Filter)

            try:
                response = llm_call([system_message]+state["messages"])
            except ValidationError as e:
                print(e.json())
                raise

            if response.is_relevant:
                filtered_reviews.append(review)

        return {"reviews":filtered_reviews}

        
    except Exception as e:

        print(f"Something went wrong during filtering reviews :\n {e}")
        raise


def rank_reviews(state:WorkerState,config:RunnableConfig):

    try:

        input_args = config["configurable"]["input_args"]

        sys_prompt=""
        with open(PROMPTS.rank/"sys_prompt.txt","r",encoding='utf-8') as file:

            sys_prompt = file.read()

        examples=""
        with open(PROMPTS.rank/"examples.txt","r",encoding='utf-8') as file:

            examples = file.read()

        filtered_reviews = []
        # Rerank the scores of reviews
        alpha = input_args["alpha"] #0.9 # 90% percent weightage to the relevance and 10% to recency
        freshness_threshold = input_args["freshness_threshold"] #90 # Threshold in days to determine the freshness of review

        for review in state["reviews"]:

            system_message = sys_prompt.format(review=review,examples=examples)
            system_message = SystemMessage(content=system_message)

            llm_call = LLM(input_args,Rank)

            try:
                response = llm_call([system_message]+state["messages"])
            except ValidationError as e:
                print(e.json())
                raise

            relevance = (response.score - 1)/9 # range 0-1
            days_passed = (date.today() - review.date.date()).days
            recency =  math.exp((-1*(days_passed))/freshness_threshold)  

            review.score = alpha*relevance + (1-alpha)*recency
       
    except Exception as e:

        print(f"Something went wrong during ranking reviews :\n {e}")
        raise
    



   



    
