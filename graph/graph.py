
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END

from graph.state import OverallState, WorkerState
from graph.nodes import (route_query, distribute_reviews, continue_to_review, 
                         process_reviews, filter_reviews, rank_reviews, consolidate_reviews)


def build_graph():

    "route to review or info"
    "process multiple reviews using send() to filter"
    "score these reviews"
    "rank them"
    "choose top 20 and then ask to answer"
    graph=None

    try:

        builder = StateGraph(state_schema=OverallState)

        builder.add_node("route_query",route_query)
        builder.add_node("distribute_reviews",distribute_reviews)
        builder.add_node("process_reviews",process_reviews)
        builder.add_node("consolidate_reviews",consolidate_reviews)

        builder.add_edge(START,"route_query")
        builder.add_conditional_edges("distribute_reviews",continue_to_review)
        builder.add_edge("process_reviews","consolidate_reviews")
        builder.add_edge("consolidate_reviews",END)

        memory = MemorySaver()
        graph = builder.compile(checkpointer=memory)

        return graph
    
    except Exception as e:

        print(f"Following exception occured while building the graph:\n {e}")
        raise


def build_review_subgraph():

    graph=None
    try:

        builder = StateGraph(state_schema=WorkerState)

        builder.add_node("filter_reviews",filter_reviews)
        builder.add_node("rank_reviews",rank_reviews)

        builder.add_edge(START,"filter_reviews")
        builder.add_edge("filter_reviews","rank_reviews")
        builder.add_edge("rank_reviews",END)

        graph = builder.compile(checkpointer=False)

        return graph

    except Exception as e:

        print(f"Following exception occured while building review graph:\n\n {e}")
        raise

    

