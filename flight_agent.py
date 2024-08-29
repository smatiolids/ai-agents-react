import json
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from langchain.prompts import PromptTemplate
from langchain.schema import AgentAction, AgentFinish, agent
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.tools.render import render_text_description
from langchain_community.chat_models import ChatOpenAI
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.tools import Tool
from typing import List
from langchain.load.dump import dumps
from callbacks import AgentCallbackHandler
from langchain.tools.retriever import create_retriever_tool
from astra_tools import get_scheduled_flights, get_flight_detail
import re
import os


# Auxiliary functions
def find_tool_by_name(tools: List[Tool], tool_name: str) -> Tool:
    for tool in tools:
        if tool.name == tool_name:
            return tool
    # raise ValueError(f"Tool wtih name {tool_name} not found")
    return False


def remove_json_comments(json_with_comments):
    """Sometimes, the JSON returned by the LLM contains comments, then it is needed to remove it"""
    comment_pattern = r'/\*.*?\*/|//.*?$'
    json_without_comments = re.sub(
        comment_pattern, '', json_with_comments, flags=re.MULTILINE)
    json_without_comments = re.sub(r"^```|```$", "", json_without_comments)
    json_without_comments = re.sub(r"^json", "", json_without_comments)
    return json_without_comments

# The Agent


class TheFlightAgent:
    agent = None
    tools = [get_scheduled_flights, get_flight_detail]

    def __init__(self):
        # https://smith.langchain.com/hub/hwchase17/react
        template = """
        Answer the following questions as best you can. You have access to the following tools:

        {tools}

        Customer ID: {customer_id}
        
        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action in JSON format without comments.
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

        Begin!

        Question: {input}
        Thought: {agent_scratchpad}
        """

        prompt = PromptTemplate.from_template(template=template).partial(
            tools=render_text_description(self.tools),
            tool_names=', '.join([t.name for t in self.tools]),
            customer_id=os.getenv("CUSTOMER_ID"),
        )

        llm = ChatOpenAI(temperature=0,
                         model_name=os.getenv("OPENAI_MODEL"),
                         stop=["\nObservation"],
                         # memory=memory,
                         callbacks=[AgentCallbackHandler()])

        self.agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_log_to_str(x["agent_scratchpad"]),
            }
            | prompt
            | llm
            | ReActSingleInputOutputParser()
        )
        print("="*50)
        print("THE FLIGHT AGENT - Initialized")
        print("="*50)

    def invoke(self, question):
        agent_step = ""
        intermediate_steps = []
        while not isinstance(agent_step, AgentFinish):
            agent_step: [AgentFinish, AgentAction] = self.agent.invoke(
                {"input": question,
                 "agent_scratchpad": intermediate_steps})

            print(agent_step)

            if isinstance(agent_step, AgentAction):
                tool_name = agent_step.tool
                tool_to_use = find_tool_by_name(self.tools, tool_name)
                tool_input = agent_step.tool_input
                print("Tool input: ", remove_json_comments(tool_input))
                observation = tool_to_use.func(
                    **json.loads(remove_json_comments(tool_input)))
                print(f"{observation=}")
                intermediate_steps.append((agent_step, str(observation)))

        if isinstance(agent_step, AgentFinish):
            print(f"Finish: {agent_step.return_values}")

        return {'content': agent_step.return_values['output']}
