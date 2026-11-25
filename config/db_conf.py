from datetime import datetime
from fastapi import FastAPI, Depends
from sqlalchemy import func, String, Float, select
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy.sql.sqltypes import DateTime

app = FastAPI()

#创建异步引擎
ASYNC_DATABASE_URL="mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb4"
async_engine=create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,#可选，输出sql日志
    pool_size=10,#设置连接池活跃的连接数
    max_overflow=20,#允许额外的连接数
)

#创建异步会话工厂
AsyncSessionLocal=async_sessionmaker(
    bind=async_engine,#绑定数据库引擎
    expire_on_commit=False,#提交会话不过期
    class_=AsyncSession#指定会话类
)
#创建依赖项
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session#返回数据库会话给路由处理函数
            await session.commit()#提交事务
        except Exception:
            await session.rollback()#有异常，全部回滚，操作不算数
            raise
        finally:
            await session.close()#关闭会话