from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from datetime import datetime

class UserOut(BaseModel):
    id: str = Field(alias="_id")
    created_at: datetime
    
    model_config = ConfigDict(populate_by_name=True)

try:
    oid = ObjectId()
    data = {
        "_id": oid,
        "created_at": datetime.now()
    }
    print(f"Testing with ObjectId: {oid}")
    user = UserOut(**data)
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")
