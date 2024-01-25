from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import asyncio
from prisma import Prisma

from typing import Optional

#JS app.use(express.json()); 과 비슷
#파싱(형변환)을 알아서 해줌
from pydantic import BaseModel
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

class Item(BaseModel):
    id: Optional[int]
    email: str
    name: str

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root(request: Request):
    print(f'found client: {request.client}')
    return templates.TemplateResponse("index.html", {"request":request})

@app.get("/hello")
def hello():
    return {
        "message": "{\
            Hello Rest API Server\
            }"
        }
#{"a":"b"} -> json이 아니라 dictionary


# path params 가져오기
# http://localhost:8000/path/2
@app.get("/path/{number}")
def get_path(number):
    print(f'path string: {number}')
    return {
        "message": "path 읽기 성공"
        }

# path params 가져오기
# http://localhost:8000/query?num=1
@app.get("/query")
def get_query(num):
    print(f'query string: {num}')
    return {
        "message": "query 읽기 성공"
        }

@app.get("/read")
def read_user():
    user = asyncio.run(read_user_db())
    return user

async def read_user_db() -> None:
    db = Prisma()
    await db.connect()

    user = await db.user.find_first(
        where={
            "name": {'contains': "홍길동"},
        }
    )
    # user = await db.user.many(
    #     where={
    #         "name": "richard",
    #     }
    # )
    print(f'found user: {user}')
    assert user is not None
    
    
    await db.disconnect()
    return user


#path
# @app.get("/path/{number}")
# def get_path(number):
#     print(f'path string: {number}')
#     return {
#         "messate":"path 읽기 성공"
#     }
#localhost:8000/path/4
    
# @app.get("/query")
# def get_query(query):
#     print(f'query string: {query}')
#     return {
#         "message": "query 읽기 성공"
#     }
#localhost:8000/query?query=4



@app.post("/create")
def create_user(item: Item):
    asyncio.run(create_user_db(item))
    return {
        "message": "쓰기 성공"
        }

async def create_user_db(item: Item) -> None:
    db = Prisma()
    await db.connect()
    item_dict = item.model_dump()
    user = await db.user.create(
        {
            'email': item_dict['email'],
            'name': item_dict['name'],
        }
    )
    print(f'created user: {user.model_dump_json(indent=2)}')

    found = await db.user.find_unique(where={'id': user.id})
    assert found is not None
    print(f'found user: {found.model_dump_json(indent=2)}')

    await db.disconnect()

@app.put("/update")
def update_user(item: Item):
    asyncio.run(update_user_db(item))
    return {
        "message": "쓰기 성공"
        }

async def update_user_db(item: Item) -> None:
    db = Prisma()
    await db.connect()
    item_dict = item.model_dump()
    user = await db.user.update(
        where={
            'id':item_dict['id'],
        },
        data={
            'email': item_dict['email'],
            'name': item_dict['name'],
        }
    )
    print(f'created user: {user.model_dump_json(indent=2)}')

    found = await db.user.find_unique(where={'id': user.id})
    assert found is not None
    print(f'found user: {found.model_dump_json(indent=2)}')

    await db.disconnect()

@app.delete("/delete/{id}")
def delete_user(id):
    id = int(id)
    asyncio.run(delete_user_db(id))
    return {
        "message": "삭제 성공"
        }

async def delete_user_db(id) -> None:
    db = Prisma()
    await db.connect()

    user = await db.user.delete(
        where={
            'id': id,
        }
    )
    await db.disconnect()