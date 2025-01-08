import json
from dataclasses import dataclass, field
from enum import IntEnum, Enum

from pydantic import BaseModel
from typing import Optional


#  租售方式
class TransactionState(IntEnum):
    UNKNOWN = 0  # 未设置
    FOR_RENT = 1  # 在租
    FOR_SALE = 2  # 在售
    FOR_TRANSFER = 3  # 转让中
    RESERVED = 10  # 已预订
    RENTED = 11  # 已租
    SOLD = 12  # 已售
    TRANSFERRED = 13  # 已转让


# 租赁方式
class RentalMethod(IntEnum):
    UNKNOWN = 0  # 未设置
    ALL = 1  # 整租
    PARTIAL = 2  # 分租
    UNSUPPORTED = 10  # 不支持出租


# 厂房类型
class FactoryType(IntEnum):
    UNKNOWN = 0  # 未设置
    STANDARD = 1  # 标准厂房
    LIGHTSTEEL = 2  # 轻钢厂房
    INDEPENDENT = 3  #  独院厂房
    PARK = 4  #  园区厂房
    SPECIAL = 5  #  特种厂房
    OTHER = 11  # 其它


# 厂房结构
class FactoryStructure(IntEnum):
    UNKNOWN = 0  # 未设置
    STEEL = 1  # 钢结构
    FRAME = 2  # 框架结构
    CONCRETE = 3  # 水泥结构
    BRICK_CONCRETE = 4  # 砖混结构
    STEEL_CONCRETE = 5  # 钢混结构
    OTHER = 11  # 其它


# 可办环评
class EIA(Enum):
    TRUE = True
    FALSE = False



class BaseHouse:
    init: bool = False
    err: str = ""
    transaction_type: list = None
    def __init__(self, data: str):
        # 尝试json化数据
        try:
            data = json.loads(data)
            self.init = True

        except:
            self.err = "错误的json格式。"
            return
        

class FACTORY(BaseModel):
    transaction_state: Optional[list[TransactionState]] = field(default_factory = list)
    rental_method: Optional[RentalMethod] = RentalMethod.UNSUPPORTED
    address: Optional[str] = ""
    factory_type: FactoryType = FactoryType.UNKNOWN

