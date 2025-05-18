from langchain_openai import ChatOpenAI



def get_llm(model_name,
            num_requests=1,
            temperature=1.0,
            tools=None,
            tool_choice="auto",
            parallel_tool_calls=False,
            response_format=None):


    llm = ChatOpenAI(
                model_name = model_name,
                temperature = temperature,
                max_tokens = 5000,
                n = num_requests,
            )


    return llm

class LLM:

    def __init__(self,args,output_format=None,tools=None):

        self.llm = get_llm(
                model_name=args["model_name"],
                num_requests=args["num_requests"],
                temperature=args["temperature"]
            )

        if(tools):
            self.llm = self.llm.bind_tools(
                                tools=tools,
                                tool_choice="auto",
                                strict=True,
                                parallel_tool_calls=False
                                )

        if(output_format):
            self.llm = self.llm.with_structured_output(output_format)    

    def __call__(self,messages):

        response = self.llm.invoke(messages)

        return response