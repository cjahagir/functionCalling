import json
import asyncio
import aiohttp
import os
from typing import Any, Dict
from pydantic import BaseModel
from agents import Agent, RunContextWrapper, FunctionTool
from openai import OpenAI

os.environ["OPENAI_API_KEY"] ="sk-proj-iFo8Z1WxtgA"

async def fetch_dashboard_data(token: str) -> Dict:
    url = "https://apis.stage.protector.sensorcon.com/dashboard/counts2"
    headers = {
        "Authorization": f"Bearer [give bearer token here, and remove brackets]"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                return await response.json()
    except Exception as e:
        return {"status": 500, "message": f"Error: {str(e)}", "data": {}}

async def ask_llm(question: str, data: Dict) -> str:
    """Send question and data to OpenAI and get a natural language response."""
    try:

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        system_prompt = "You are an AI assistant that helps users understand dashboard data about protectors and calistations. Provide direct, concise answers based on user querry."
        user_prompt = f"""
        Here's the current dashboard data:
        ```json
        {json.dumps(data, indent=2)}
        ```
        
        The user asks: "{question}"
        
        Please provide a natural language response that directly answers the question based on the data.
        Keep your response concise.Give the API response related data only if user asks about it
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")

async def run_dashboard_fetch(ctx: RunContextWrapper[Any], args: str) -> str:
    token = "eyJraWQiOiJUZXhaMk1IT1owWG81VWdQbU5kU3NUallnQXZGTVliRlJnY252QnE3ZytvPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzNGU4NDQyOC05MDcxLTcwOGUtZTY0MC0yMGFiOWExOGEwZjQiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9nME5KNWtJbTkiLCJjbGllbnRfaWQiOiJwY245dmxmOGdxcTFzOHJmNnQydHUwaTBjIiwib3JpZ2luX2p0aSI6IjNhMGFiYWRiLTM2NGUtNDAyYi1hNDg3LWM2NjFkZjE1NDQ4MSIsImV2ZW50X2lkIjoiN2ExZGE1MzktZWEyYi00ZjExLThiODUtYTQwYTY2Y2VlZmIzIiwidG9rZW5fdXNlIjoiYWNjZXNzIiwic2NvcGUiOiJhd3MuY29nbml0by5zaWduaW4udXNlci5hZG1pbiIsImF1dGhfdGltZSI6MTc0NTU4NTU1OSwiZXhwIjoxNzQ1NTg5MTU5LCJpYXQiOjE3NDU1ODU1NTksImp0aSI6IjBjYWE2YjVlLTc5MDAtNGU0OS1iNjk3LWQ5MTkxNjUzYjdlYyIsInVzZXJuYW1lIjoiMzRlODQ0MjgtOTA3MS03MDhlLWU2NDAtMjBhYjlhMThhMGY0In0.lS5OeuAU2nxWOJFpe_M2-kHwvrsE8zdszp_e8v0XSJg0tCVxPJUuCQCGI3INWxThZ47Ey9uPsVYbyCdEp-VqJ5XtTLzJ8DEhbaUP-A7ny-eqScyWfFGur8huVZedZqpSra3jst3O0pgaB7G61_IA_PzLR618gGFVv5r_mRHN132IraUXAEyhxMPHPTgC3D7JpKyLtrVqNrktTHlxX0YHyzOo2bdI_u4nN-j_30DZikMUDwjjx2RNFEvZ5bA0KURM6NvdTuHn22hvvZqmjA7NhIeSBJdzvrf5S7RzRmTqmzsQ69qGGxHAmw_1A42k3pFGEcrFPinH5LcRLcJpCtXqFg"
    data = await fetch_dashboard_data(token)
    question = ctx.get("user_query",)
    response = await ask_llm(question, data)
    return response

dashboard_tool = FunctionTool(
    name="fetch_dashboard_counts",
    description="Fetch dashboard counts data from the Protector Sensorcon API.",
    params_json_schema={},
    on_invoke_tool=run_dashboard_fetch,
)

class DashboardLLMAgent:
    def __init__(self):
        self.agent = Agent(
            name="ProtectorDashboardAgent",
            tools=[dashboard_tool],
        )
        
    async def process_query(self, query: str) -> str:
        token = "abc"
        data = await fetch_dashboard_data(token)
        return await ask_llm(query, data)

async def main():
    dashboard_agent = DashboardLLMAgent()
    
    for tool in dashboard_agent.agent.tools:
        if isinstance(tool, FunctionTool):
            print(tool.name)
            print(tool.description)
            print(json.dumps(tool.params_json_schema, indent=2))
            print()
    
    print("Ask questions about the dashboard data (type 'exit' to quit):")
    
    while True:
        user_input = input("> ")
        if user_input.lower() == "exit":
            break
        
        response = await dashboard_agent.process_query(user_input)
        print(response)

if __name__ == "__main__":
    asyncio.run(main())
