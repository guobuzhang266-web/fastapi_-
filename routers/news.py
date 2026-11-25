from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.params import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from crud import news
from config.db_conf import get_db


#创建APIRouter实例
router = APIRouter(prefix="/api/news",tags=["news"])


#获取新闻分类列表
@router.get("/categories")
async def get_categories(db:AsyncSession=Depends(get_db),
                         skip: int = 0,
                         limit: int = 100,
                         ):
    #调用CRUD函数获取分类列表
    categories=await news.get_categories(db, skip, limit)
    return {
        "code": 200,
        "message":"获取分类列表成功",
        "data":categories
    }


#获取新闻列表
@router.get("/list")
async def get_news(category_id:int=Query(...,alias="categoryId"),
                   page:int=1,
                   page_size:int=Query(10,alias="pageSize",le=100),
                   db:AsyncSession=Depends(get_db)):
    #调用CRUD函数获取新闻列表
    offset = (page-1)*page_size
    #查询指定分类下的新闻列表
    news_list=await news.get_news_list(db, category_id, offset, page_size)
    #查询指定分类下的新闻所有数量
    total=await news.get_news_count(db, category_id)
    #判断是否有更多数据
    has_More=(offset + len(news_list)) < total
    return {
        "code": 200,
        "message":"获取新闻列表成功",
        "data":{
            "list":news_list,
            "total":total,
            "hasMore":has_More
        }
    }


#获取新闻详情
@router.get("/detail")
async def get_news_detail(news_id:int=Query(...,alias="id"),
                         db:AsyncSession=Depends(get_db)):
    #调用CRUD函数获取新闻详情
    news_detail= await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(404,detail="新闻不存在")
    #调用CRUD函数增加新闻浏览量
    success_query = await news.increase_news_views(db, news_id)
    if not success_query:
        raise HTTPException(404,detail="新闻不存在")
    #调用CRUD函数获取同类新闻
    related_news=await news.get_related_news(db, news_id, news_detail.category_id)

    return {
        "code": 200,
        "message":"获取新闻详情成功",
        "data":{
            "id":news_detail.id,
            "title":news_detail.title,
            "content":news_detail.content,
            "image":news_detail.image,
            "author":news_detail.author,
            "publishTime":news_detail.publish_time,
            "categoryId":news_detail.category_id,
            "views":news_detail.views,
            "relatedNews":related_news
        }
    }

