from typing import List, Optional
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
    url: Optional[str] = None
    posts: Optional[List[Post]] = None
