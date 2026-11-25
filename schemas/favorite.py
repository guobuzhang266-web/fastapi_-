from dataclasses import Field
import datetime
from pydantic import BaseModel, ConfigDict
from schemas.base import News


# 收藏检查响应模型
class FavoriteCheckResponse(BaseModel):
    is_favorite: bool=Field(...,alias="is_favorite")

# 添加收藏新闻请求模型
class FavoriteNewsRequest(BaseModel):
    news_id: int=Field(...,alias="newsId")

class FavoriteNewsResponse(News):
    favorite_id:int=Field(alias="favoriteId")
    favorite_time:datetime=Field(alias="favoriteTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

# 收藏新闻列表响应模型
class FavoriteListResponse(BaseModel):
   list: list[FavoriteNewsResponse]
   total: int
   has_more: bool=Field(...,alias="hasMore")

   model_config = ConfigDict(
       populate_by_name=True,
       from_attributes=True
   )


