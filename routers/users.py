from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from config.db_conf import get_db
from crud.users import get_user_by_username, create_user, create_token, authenticate, update_user_info, \
    update_user_password
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UpdateUserInfoRequest, UpdatePasswordRequest
from utils.auth import get_current_user
from utils.responese import success_response

router = APIRouter(prefix="/api/users", tags=["users"])

#用户注册
@router.post("/register")
async def register(user_data:UserRequest, db:AsyncSession=Depends(get_db)):
    """注册逻辑：检验用户是否存在→不存在,创建用户→返回用户令牌"""
    #检验用户是否存在
    existing_users=await get_user_by_username(db, user_data.username)
    if existing_users:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    #创建用户
    user=await create_user(db, user_data)   #返回的user是一个orm的对象
    #创建token
    user_token=await create_token(db,user.id)
    response_data=UserAuthResponse(token=user_token,user_info=UserInfoResponse.model_validate(user))
    return success_response(message="用户注册成功",data=response_data)

#用户登录
@router.post("/login")
async def login(user_data:UserRequest, db:AsyncSession=Depends(get_db)):
    """登录逻辑：检验用户是否存在→存在,检验密码→正确,返回用户令牌"""
    user= await authenticate(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    #创建token
    user_token=await create_token(db,user.id)
    response_data=UserAuthResponse(token=user_token,user_info=UserInfoResponse.model_validate(user))
    return success_response(message="用户登录成功",data=response_data)

#用户信息
@router.get("/info")
async def info(user=Depends(get_current_user)):#依赖注入，自动获取当前登录用户
    return success_response(message="获取用户信息成功",data=UserInfoResponse.model_validate(user))

#更新用户信息
@router.put("/info")
async def update_info(user_data:UpdateUserInfoRequest,
                      user=Depends(get_current_user),
                      db:AsyncSession=Depends(get_db)):
    """更新用户信息"""
    new_user=await update_user_info(db, user.username, user_data)
    return success_response(message="更新成功",data=UserInfoResponse.model_validate(new_user))

#修改用户密码
@router.put("/password")
async def update_password(user_data:UpdatePasswordRequest,
                          user=Depends(get_current_user),
                          db:AsyncSession=Depends(get_db)):
    updated_user=await update_user_password(db, user,user_data.old_password,user_data.new_password)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="密码更新失败")
    return success_response(message="密码更新成功")







