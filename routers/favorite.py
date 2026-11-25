from fastapi import APIRouter, Query, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud.favorite import is_news_favorited, add_favorite_news, remove_favorite_news, get_favorite_list, \
    clear_favorite_news
from models.users import User
from schemas.favorite import FavoriteCheckResponse, FavoriteNewsRequest, FavoriteListResponse
from utils.auth import get_current_user
from utils.responese import success_response

router = APIRouter(prefix="/api/favorite", tags=["favorite"])

# 收藏检查接口
@router.get("/check")
async def check_favorite(db:AsyncSession=Depends(get_db),
                         user:User=Depends(get_current_user),
                         news_id:int=Query(...,alias="newsId")):
    # 检查用户是否收藏了该新闻
    is_favorited = await is_news_favorited(db, user.id, news_id)
    return success_response(message="检查结果成功",data=FavoriteCheckResponse(is_favorite=is_favorited))

# 添加收藏新闻接口
@router.post("/add")
async def add_favorite(data:FavoriteNewsRequest,
                       db:AsyncSession=Depends(get_db),
                       user:User=Depends(get_current_user),
                       ):
    #添加新闻
    favorite = await add_favorite_news(db, user.id, data.news_id)
    return success_response(message="收藏成功",data=favorite)

# 取消收藏新闻接口
@router.post("/remove")
async def remove_favorite(db:AsyncSession=Depends(get_db),
                          user:User=Depends(get_current_user),
                          news_id:int=Query(...,alias="newsId")):
    # 取消收藏新闻
    is_removed = await remove_favorite_news(db, user.id, news_id)
    if not is_removed:
        raise HTTPException(status_code=404,detail="收藏不存在")
    return success_response(message="取消收藏成功")

# 获取收藏新闻列表接口
@router.get("/list")
async def get_favorite(db:AsyncSession=Depends(get_db),
                       user:User=Depends(get_current_user),
                       page:int=Query(1,ge=1),
                       page_size:int=Query(10,alias="pageSize")):
    # 获取收藏新闻列表
    rows,total = await get_favorite_list(db, user.id, page, page_size)
    # 转换为json格式
    favorite_list = [
        {
            **news.__dict__,
            "favorite_id":favorite_id,
            "favorite_time":favorite_time
        }
        for news,favorite_id,favorite_time in rows
    ]
    has_more=total>page*page_size
    data=FavoriteListResponse(list=favorite_list,total=total,has_more=has_more)
    return success_response(message="收藏新闻列表成功",data=data)

#清空收藏
@router.delete("/clear")
async def remove_favorite(db:AsyncSession=Depends(get_db),
                          user:User=Depends(get_current_user)):
    # 清空收藏新闻
    is_removed = await clear_favorite_news(db, user.id)
    return success_response(message=f"清空收藏{is_removed}条")

#


