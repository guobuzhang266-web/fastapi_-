from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
def success_response(message:str="success",data=None):
    content={
        "code":200,
        "message":message,
        "data":data
    }
    #jsonable_encoder把任何的pydantic，orm对象转换为普通的python字典，列表等格式
    return JSONResponse(content=jsonable_encoder(content))
