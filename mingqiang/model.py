from datetime import datetime, timezone
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, BigInteger, Float, Boolean, Text, DateTime, ForeignKey

from mingqiang import db


class User(db.Model):
    # 设置表名
    __tablename__ = "users"
    # 设定字段
    id = Column(BigInteger, primary_key = True, unique = True, nullable = False)  # 使用19位SnowId
    openid = Column(String(32), nullable = False)  # 微信用户唯一标识
    nickname = Column(String(32), nullable = False, default = "未命名")
    avatar = Column(String(128), nullable = False, default = "")
    supervisor = Column(Boolean, nullable = False, default = False)
    groups = db.relationship("Group", secondary = "usergroupships", back_populates = "members")
    houses = db.relationship("House", backref = db.backref("owner"))
    collections = db.relationship("House", secondary = "usercollectionships", back_populates = "collectors")

    created_at = Column(DateTime, nullable = False, default = datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable = False, default = datetime.now(timezone.utc), onupdate = datetime.now(timezone.utc))

class Group(db.Model):
    # 设置表名
    __tablename__ = "groups"
    # 设定字段
    id = Column(Integer, primary_key = True, unique = True, nullable = False)
    name = Column(String(16), nullable = False)
    members = db.relationship("User", secondary = "usergroupships", back_populates = "groups")
    houses = db.relationship("House", backref = db.backref("group"))


class House(db.Model):
    # 设置结构体表格名称
    __tablename__ = "houses"
    # 设定结构体对应表格的字段
    id = Column(BigInteger, primary_key = True, unique = True, nullable = False)
    title = Column(String(30), nullable = False)  # 房源标题，用于展示
    house_type = Column(Integer, nullable = False)  # 1-商铺 2-写字楼 3-厂房
    transaction_type = Column(Integer, nullable = False)  # 1-出售 2-出租
    transfer_type = Column(Integer, default = 0)  # 如果出租，是否转让 1-是 2-否
    rent_type = Column(Integer, default = 0)  # 如果厂房，如果出租 1-整租 2-分组
    property = Column(Integer, nullable = False, default = 0)  # 1-新房 2-二手房
    # 类型，不同类型房源含义不同
    # 商铺 1-商业街店铺 2-写字楼配套 3-社区底商 4-临街门面 5-档口摊位 6-购物/百货中心 99-其它
    # 写字楼 1-纯写字楼 2-商业综合体 3-商务公寓 4-商务酒店 5-产业园区 99-其它
    # 厂房 1-标准厂房 2-轻钢厂房 3-独院厂房 4-园区厂房 5-特种厂房 99-其它
    detailed_property = Column(Integer, nullable = False, default = 0)
    # 厂房结构 1-框架结构 2-钢结构 3-水泥结构 4-钢混结构 5-砖混结构 99-其它
    factory_structure = Column(Integer, nullable = False, default = 0)
    eia = Column(Integer, nullable = False, default = 0)  # 如果厂房，可办环评 1-是 2-否
    office_name = Column(String(30), nullable = False, default = "")  # 如果办公楼，写字楼名称
    address_region = Column(String(50), nullable = False, default = "")  # 地址-区域 精确到街道 以逗号分割
    address_detail = Column(String(30), nullable = False, default = "")  # 地址-详细地址
    business_status = Column(Integer, nullable = False, default = 0)  # 如果商铺，经营状况 1-经营中 2-空置中
    area_building = Column(Float, nullable = False, default = 0)  # 建筑面积，以m²为单位
    area_usable = Column(Float, nullable = False, default = 0)  # 使用面积，以m²为单位
    floor = Column(Integer, nullable = False, default = 0)  # 1-单层 2-多层 3-独栋
    # 楼层信息 总层数，层数，首层/该层数据
    floor_data = Column(String(100), nullable = False, default = "")
    decoration = Column(Integer, nullable = False, default = 0)  # 1-毛坯 2-简装 3-精装修 4-豪华装修
    ownership = Column(Integer, nullable = False, default = 0)  # 1-个人持有 2-开发商持有 3-公司持有 99-其它
    rent_price = Column(Float, nullable = False, default = 0)  # 价格 单位：万元/月
    min_lease_term = Column(Integer, nullable = False, default = 0)  # 起租期 单位：月
    sale_price = Column(Float, nullable = False, default = 0)  # 价格 单位：万元
    home_owner = Column(String(50), nullable = False, default = ",")  # 房主称呼及联系方式，以逗号分割
    notes = Column(Text, nullable = False, default = "")  # 房源备注
    images = Column(Text, nullable  = False, default = "")  # 图片
    videos = Column(Text, nullable = False, default = "")  # 视频

    removed = Column(Boolean, nullable = False, default = False)  # 已下架

    owner_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable = False)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable = False)
    collectors = db.relationship("User", secondary = "usercollectionships", back_populates = "collections")

    raw = Column(Text, nullable = False, default = "")
    created_at = Column('createdAt', DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column('updatedAt', DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate = datetime.now(timezone.utc))


# 关系表
class UserGroupShip(db.Model):
    # 设置表名
    __tablename__ = "usergroupships"
    # 设定字段
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key = True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key = True)
    role = Column(Integer, nullable = False, default = 0)  # 0-成员 1-管理员 2-创建者

class UserCollectionShip(db.Model):
    # 设置表名
    __tablename__ = "usercollectionships"
    # 设定字段
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key = True)
    house_id = Column(BigInteger, ForeignKey("houses.id", ondelete="CASCADE"), primary_key = True)
