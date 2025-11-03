from typing import List
from pydantic import BaseModel


class Article(BaseModel):
    timePublishedMillis: int
    timePublished: str
    headline: str
    vignette: str
    articleType: str
    category: str
    newsSource: str
    fullArticleLink: str
    intro: str
    externalLink: bool


class News(BaseModel):
    articles: List[Article]
    moreNewsLink: str
