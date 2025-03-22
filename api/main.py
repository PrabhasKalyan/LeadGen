import json
from fastapi import FastAPI
import os
from dotenv import load_dotenv
load_dotenv()
import langgraph.graph
from openai import OpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
import langgraph as lg
from langgraph.graph import Graph,END
from langchain.schema import HumanMessage,AIMessage

os.environ["TAVILY_API_KEY"] = "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"

client = OpenAI(
    api_key="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",
    base_url = "https://api.groq.com/openai/v1",
)

search = TavilySearchResults(max_results=2)
app=FastAPI()



def search1(state):
    prompt= state["messages"][-1].content
    prompt = prompt  + "\nAnalyze the following query and determine whether it requires a web search to answer accurately. Return only 'Yes' if a web search or real-time data is needed, otherwise return 'No'. Do not provide any explanation or additional text."  
    response = client.chat.completions.create(
        model="llama3-8b-8192",
         messages=[
        {"role": "user", "content":prompt}]
        )
    state = {"messages": state["messages"], "decision": response.choices[0].message.content}
    return state


def websearch(state):
    prompt= state["messages"][-1].content
    search_results = search.invoke(prompt)
    response = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {"role": "user", "content":f"Analyse this {search_results}and answer the question :{prompt} Do not provide any explanation or additional text just give me the answer "}
    ])
    state={"messages": state["messages"] + [AIMessage(response.choices[0].message.content)]}
    print(state["messages"][-1].content)
    return state


def llm_search(state):
    prompt= state["messages"][-1].content
    prompt = prompt  + "\n Do not provide any explanation or additional text just give me the answer"  
    response = client.chat.completions.create(
        model="llama3-8b-8192",
         messages=[
        {"role": "user", "content":prompt}]
        )
    print(response.choices[0].message.content)
    state={"messages": state["messages"] + [AIMessage(response.choices[0].message.content)]}
    return state



workflow = Graph()
workflow.add_node("search_test",search1)
workflow.add_node("websearch",websearch)
workflow.add_node("llm_search",llm_search)

workflow.add_conditional_edges("search_test",
                               lambda state:state["decision"],{
                                   "Yes":"websearch",
                                   "No":"llm_search"
                               })


workflow.set_entry_point("search_test")
workflow.add_edge("websearch", END)
workflow.add_edge("llm_search", END)
workflow_app=workflow.compile()


@app.post("/websearch")
def start(prompt):
    state = {"messages": [HumanMessage(content=prompt)]}
    output = workflow_app.invoke(state)
    print(output["messages"][-1].content)
    return output["messages"][-1].content








