from typing import Optional
from pydantic import BaseModel


class Post(BaseModel):
    author: str
    title: str
    content: str
    likes: int
    replies: int
    timestamp: int
    url: str


class ForumPosts(BaseModel):
    url: Optional[str]
    posts: Optional[Post]
