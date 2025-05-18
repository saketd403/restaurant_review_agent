from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


from util import set_env
from graph.graph import build_graph



def run():

    input_args = {
        "model_name":"gpt-4o",
        "num_requests":1,
        "temperature":0.2,
        "restaurant_id":"ljxNT9p0y7YMPx0fcNBGig",
        "max_workers":1,
        "alpha":0.9,
        "freshness_threshold":90,
        "top_k":20
    }
    #user_query = "How is their bacon white pasta?"

    set_env("OPENAI_API_KEY")

    config = {"configurable": {"thread_id": "1", "input_args":input_args}}

    graph = build_graph()

    messages=[]
    while True:

        try:

            user_input = input("User: ")

            if user_input.lower() in ["quit", "exit", "q"]:
                print(f"Assistant:\nGoodbye!")
                break

            messages.append(HumanMessage(content=user_input,name="user"))

            response = graph.invoke(
                            {
                                "messages":messages
                            },
                            config=config
                        )

            print(f"Assistant:\n{response["answer"]}")

            messages=[]
            messages.append(AIMessage(content=response["answer"],name="assistant"))

        except Exception as e:

            print(f"Following exception occured during graph run {e}")


if __name__ == "__main__":

    run()
