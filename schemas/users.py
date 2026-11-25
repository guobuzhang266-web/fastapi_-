from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class UserRequest(BaseModel):
    """
    ⽤户必要信息
    """
    username: str
    password: str

class UserInfoBase(BaseModel):
    """
    ⽤户信息基础数据模型
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个⼈简介")

class UserInfoResponse(UserInfoBase):
    """
    ⽤户信息响应数据模型
    """
    id:int
    username: str

    model_config = ConfigDict(
        from_attributes=True  # 允许从orm对象属性中取值
    )


#data数据类型
class UserAuthResponse(BaseModel):
    token: str
    user_info:UserInfoResponse=Field(..., alias="userInfo")

    #模型类配置
    model_config = ConfigDict(
        populate_by_name=True,#  alias/字段名兼容
        from_attributes=True # 允许从orm对象属性中取值
    )

#更新用户的模型类
class UpdateUserInfoRequest(BaseModel):
    nickname:str=None
    avatar:str=None
    gender:str=None
    bio:str=None
    phone:str=None

#更新用户密码
class UpdatePasswordRequest(BaseModel):
    old_password:str=Field(..., alias="oldPassword",description="旧密码")
    new_password:str=Field(..., alias="newPassword",description="新密码")




