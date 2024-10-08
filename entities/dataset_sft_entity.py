from pydantic import BaseModel

from utils.encoder import jsonable_encoder


class DatasetsTextSFTFormat(BaseModel):
    instruction:str=""
    input:str=""
    output:str=""

    def to_dict(self) -> dict:
        return jsonable_encoder(self)