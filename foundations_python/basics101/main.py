from pydantic import BaseModel, ValidationError
from datetime import datetime


class User(BaseModel):
    uid:int
    username:str
    email:str
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

