import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.users import User, UserToken
from schemas.users import UserRequest, UpdateUserInfoRequest, UpdatePasswordRequest
from utils.security import get_hash_password, verify_password


#根据用户名查询用户
async def get_user_by_username(db: AsyncSession, username: str):
    query=select(User).where(User.username == username)
    result=await db.execute(query)
    return result.scalar_one_or_none()

#创建用户
async def create_user(db: AsyncSession, user_data:UserRequest):
    #密码加密
    hashed_password=get_hash_password(user_data.password)
    user=User(username=user_data.username,password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)#刷新用户对象，确保返回的是最新数据
    return user

#创建token
async def create_token(db:AsyncSession,user_id:int):
    #生成token
    token=str(uuid.uuid4())
    #设置token过期时间7天
    expires_at=datetime.now()+timedelta(days=7)
    #检查用户是否已有token（user_id 不唯一，可能有多条，取第一条避免 MultipleResultsFound）
    query=select(UserToken).where(UserToken.user_id == user_id).order_by(UserToken.id).limit(1)
    result=await db.execute(query)
    user_token=result.scalars().first()
    #如果用户已有token，更新token和过期时间
    if user_token:
        #sqlalchemy异步session的追踪机制（脏检查），会自动检测到token字段的更新，无需手动刷新
        user_token.expires_at=expires_at
        user_token.token=token
    else:
        #如果用户没有token，创建新token
        user_token=UserToken(user_id=user_id,token=token,expires_at=expires_at)
        db.add(user_token)
    #新增和更新都要提交，统一放到 if/else 外面只提交一次
    await db.commit()
    return token

#用户登录
async def authenticate(db:AsyncSession, username:str, password:str):
    user=await get_user_by_username(db, username)
    if not user:
        return None
    password_valid=verify_password(password, user.password)
    if not password_valid:
        return None
    return user

#根据token查询用户:验证token→查询用户→返回用户对象
async def get_user_by_token(db:AsyncSession, token:str):
    token_query=select(UserToken).where(UserToken.token==token)
    result=await db.execute(token_query)
    user_token=result.scalar_one_or_none()
    if not user_token or user_token.expires_at < datetime.now():
        return None
    #token查询用户
    user_query=select(User).where(User.id==user_token.user_id)
    result=await db.execute(user_query)
    return result.scalar_one_or_none()

#更新用户信息
async def update_user_info(db:AsyncSession, username:str, user_data:UpdateUserInfoRequest):
    """更新用户信息"""
    update_user=update(User).where(User.username == username).values(**user_data.model_dump(exclude_unset=True,
                                                                                exclude_none=True))
    result=await db.execute(update_user)
    await db.commit()
    #判断是否命中
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")
    #获取更新后的用户对象
    new_user=await get_user_by_username(db, username)
    return new_user

#修改用户密码
async def update_user_password(db:AsyncSession, user:User, old_password:str, new_password:str):
    """修改用户密码"""
    #验证旧密码
    if not verify_password(old_password, user.password):
        return False
    #更新新密码
    user.password=get_hash_password(new_password)
    db.add(user)#由sqlalchemy真正接管这个对象，可以确保成功提交  规避session过期或者关闭导致不能提交的问题
    await db.commit()
    await db.refresh(user)#刷新用户对象，确保返回的是最新数据
    return True














