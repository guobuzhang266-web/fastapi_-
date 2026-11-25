from fastapi import FastAPI
from routers import news, users, favorite
from fastapi.middleware.cors import CORSMiddleware
from utils.exception_handlers import register_exception_handlers

#创建FastAPI实例
app=FastAPI()

#注册全局异常处理器
register_exception_handlers(app)

#添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message":"Hello World"}

#挂载新闻路由
app.include_router(news.router)

#挂载用户路由
app.include_router(users.router)

#挂载收藏路由
app.include_router(favorite.router)
