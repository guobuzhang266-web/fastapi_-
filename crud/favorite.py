from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.favorite import Favorite
from models.news import News


# 检查用户是否收藏了该新闻
async def is_news_favorited(db: AsyncSession, user_id: int, news_id: int) -> bool:
    query = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(query)
    return result.one_or_none() is not None

# 添加收藏新闻
async def add_favorite_news(db: AsyncSession, user_id: int, news_id: int):
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

# 取消收藏新闻
async def remove_favorite_news(db: AsyncSession, user_id: int, news_id: int):
    query = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result= await db.execute(query)
    await db.commit()
    return result.rowcount>0

# 获取收藏新闻列表
async def get_favorite_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10):
    #统计收藏新闻总数
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total=count_result.scalar_one()
    #联表查询收藏新闻列表
    #select(查询主体模型类，联合查询表的字段.label("别名")).join(联合查询模型类,联合查询条件).where(主查询条件)
    offset=(page-1)*page_size
    list_query = (select(News,Favorite.news_id.label("favorite_id"),Favorite.created_at.label("favorite_time")).
             join(Favorite,News.id == Favorite.news_id).
             where(Favorite.user_id == user_id).
             order_by(Favorite.created_at.desc()).
             offset(offset).
             limit(page_size))
    #返回的结果是一个列表，里面是一个个的元组，每个元组的字段由news表里面的所有字段和favorite表里面的收藏时间和收藏id组成
    list_result = await db.execute(list_query)
    favorite_list=list_result.all()
    return favorite_list,total

# 清空收藏新闻
async def clear_favorite_news(db: AsyncSession, user_id: int):
    query = delete(Favorite).where(Favorite.user_id == user_id)
    result= await db.execute(query)
    await db.commit()
    return result.rowcount or 0
