from fastapi import FastAPI
from fastapi import Request, HTTPException, status, requests
from pydantic import BaseModel, ValidationError
from typing import Optional
import httpx
import asyncio
import json

###### LANGCHAIN IMPORTS ######
from langchain.agents import initialize_agent, AgentType, load_tools
from langchain_community.chat_models import ChatOpenAI
from langchain.globals import set_verbose

###### OPENAI IMPORTS ######
from openai import OpenAI

###### CUSTOM IMPORTS ######
from functions import get_stock_price, get_weather

# FastAPI app initialization
app = FastAPI()

class UserInput(BaseModel):
    user_input: str
    openai_api_key: str

class ImageRequest(BaseModel):
    prompt: str
    size: str
    quality: str
    n: int
    openai_api_key: str

class ChatRequest(BaseModel):
    prompt_type: str
    user_message: str
    system_prompt: str
    max_tokens: Optional[int] 
    presence_penalty: Optional[float] 
    temperature: Optional[float] 
    top_p: Optional[float] 
    openai_api_key: str

class Gpt16kRequest(BaseModel):
    prompt_type: str
    user_message: str
    system_prompt: str
    max_tokens: Optional[int] 
    presence_penalty: Optional[float] 
    temperature: Optional[float] 
    top_p: Optional[float] 
    openai_api_key: str    

class WebchatRequest(BaseModel):
    user_input: str
    openai_api_key: str
    thread_id: Optional[str]
    assistant_id: str


@app.post("/get-response/")
async def get_response(input: UserInput):
    OPENAI_API_KEY = input.openai_api_key
    set_verbose(True)
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106", api_key=OPENAI_API_KEY)
    tools = load_tools(["ddg-search"], llm=llm)
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
    response = agent.invoke(input.user_input)
    return {"response": response}


@app.post("/generate-image/")
async def generate_image_endpoint(image_request: ImageRequest):
    client = OpenAI(api_key=image_request.openai_api_key)
    try:
        response = client.images.generate(
            model="dall-e-3", 
            prompt=image_request.prompt, 
            size=image_request.size, 
            quality=image_request.quality, 
            n=image_request.n
        )
        return {"image_url": response.data[0].url} if response.data else {"error": "No image generated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def chat_three_async(chat_request: ChatRequest):
    try:
        client = OpenAI(api_key=chat_request.openai_api_key)
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": chat_request.system_prompt},
                {"role": "user", "content": chat_request.user_message}
            ],
            max_tokens=chat_request.max_tokens,
            presence_penalty=chat_request.presence_penalty,
            temperature=chat_request.temperature,
            top_p=chat_request.top_p
        )
        return completion.choices[0].message.content
    except Exception as e:
        return str(e)

@app.post("/chat_three")
async def chat_with_gpt(request: Request):
    chat_request = await request.json()
    chat_request_model = ChatRequest(**chat_request)
    response = await chat_three_async(chat_request_model)
    return {"response": response}



async def gpt16k_async(chat_request: Gpt16kRequest):
    try:
        client = OpenAI(api_key=chat_request.openai_api_key)
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": chat_request.system_prompt},
                {"role": "user", "content": chat_request.user_message}
            ],
            max_tokens=chat_request.max_tokens,
            presence_penalty=chat_request.presence_penalty,
            temperature=chat_request.temperature,
            top_p=chat_request.top_p
        )
        return completion.choices[0].message.content
    except Exception as e:
        return str(e)

@app.post("/gpt16k")
async def chat_with_gpt(request: Request):
    chat_request = await request.json()
    chat_request_model = Gpt16kRequest(**chat_request)
    response = await gpt16k_async(chat_request_model)
    return {"response": response}


async def webchat_async(webchat_request: WebchatRequest):

    thread = webchat_request.thread_id
    user_input = webchat_request.user_input
    assistant_id = webchat_request.assistant_id
    openai_api_key = webchat_request.openai_api_key

    if not thread:
        client = OpenAI(api_key=openai_api_key)
        thread = client.beta.threads.create()
        thread_id = thread.id

        client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_input)
        run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)    

    while True:
        await asyncio.sleep(5)

        # Retrieve the run status
        run_status = client.beta.threads.runs.retrieve(
          thread_id=thread_id,
          run_id=run.id
         )    
        
        if run_status.status == 'completed':
          messages = client.beta.threads.messages.list(
              thread_id=thread_id
          )

          
          for msg in messages.data:
              role = msg.role
              content = msg.content[0].text.value
              print(f"{role.capitalize()}: {content}")

          break

        elif run_status.status == 'requires_action':

          required_actions = run_status.required_action.submit_tool_outputs.model_dump()

          tool_outputs = []

          for action in required_actions["tool_calls"]:
              func_name = action['function']['name']
              arguments = json.loads(action['function']['arguments'])

              if func_name == "get_stock_price":
                  output = get_stock_price(symbol=arguments['symbol'])
                  tool_outputs.append({
                      "tool_call_id": action['id'],
                      "output": output
                  })
              elif func_name == "get_weather":
                  output = get_weather(location=arguments['location'])
                  tool_outputs.append({
                      "tool_call_id": action['id'],
                      "output": output
                  })   

              else:
                  raise ValueError(f"Unknown function: {func_name}")


          client.beta.threads.runs.submit_tool_outputs(
              thread_id=thread_id,
              run_id=run.id,
              tool_outputs=tool_outputs
          )
        else:
            print("Waiting for the Assistant to process...")
            await asyncio.sleep(5)

    # Retrieve and return the latest message from the assistant
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages.data[0].content[0].text.value


    return ({"response": response})

@app.post("/webchat")
async def chat_with_webchat(request: Request):
    webchat_request = await request.json()
    webchat_request_model = WebchatRequest(**webchat_request)
    response = await webchat_async(webchat_request_model)
    return response