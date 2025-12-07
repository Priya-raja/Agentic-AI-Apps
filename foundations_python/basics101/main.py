from pydantic import BaseModel, ValidationError,Field
from datetime import datetime,UTC
from functools import partial
#partial allows to prefill some values of a function and generate a new function

from typing import Literal,Annotated


class User(BaseModel):
    uid:Annotated [int, Field(gt=0)]
    username:Annotated [str, Field(min_length=3, max_length=50)]
    email:str
    age:Annotated [int,Field(ge=13, le=120)]
    bio: str= ""
    verified_at: datetime | None = None
    is_active: bool = True
    full_name: str | None = None

try:
   user = User(
            uid=1,
            username="john_doe",
            email= "jonny@gmail.com"
            ) 
except ValidationError as e:
    print("Error:", e) 
    user = None
else:
    print(user.model_dump_json(indent=2))    




# Accessing attributes
# print(user.username)
# user.bio = "Python Developer"


# Convert to. a dictionary
# user_dict = user.model_dump()
# print(user_dict)

# Convert to json
# user_json = user.model_dump_json(indent = 2)
# print(user_json)

# model_dump is Useful to serialize means easily set to a format wanted.

class BlogPost(BaseModel):
    id: int
    title: Annotated[str, Field(min_length=1, max_length=200)]
    content: Annotated[str, Field(min_length=10)]
    is_published:bool = False
    tags:list[str]= Field(default_factory=list)
    # created_at: datetime = Field(default_factory = lambda: datetime.now(tz=UTC))
    created_at: datetime = Field(default_factory=partial(datetime.now, tz=UTC))

    author_id : str | int

    #restricts the value of status to only these three options and no other than this. Thst's called Literal type

    status: Literal["draft", "published", "archived"] = "draft"
    slug :Annotated[str, Field(pattern=r"^[a-z0-9-]+ $")] 


# post = BlogPost(
#     id=101,
#     title="My First Blog Post",
#     content="This is the content of my first blog post.",
#     author_id="123",
#     tags=["python", "programming", "tutorial"],
#     status="published",
# )
try: 
    user1 = User(
            uid=0,
            username="jd",
            email="")
except ValidationError as e:
    print("Error:", e) 
    user1 = None

# print(post.model_dump_json(indent=2))
print(user1)