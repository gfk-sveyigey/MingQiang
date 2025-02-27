from mingqiang.model import User, Group, House, UserCollectionShip
from mingqiang import db, app, house_id_generator, user_id_generator
from mingqiang import services
from typing import Union
from sqlalchemy import or_, and_
import json

def get(id: int) -> Union[House, None]:
    house = House.query.get(id)
    return house

def get_all() -> list:
    houses = House.query.all()
    return houses

def new_id() -> int:
    return house_id_generator.generate()

def new(data: dict) -> House:
    house = House(
        id = int(data["id"]),
        title = data["title"],
        house_type = data["houseType"],
        transaction_type = data["transactionType"],
        transfer_type = data["transferType"],
        rent_type = data["rentType"],
        property = data["property"],
        detailed_property = data["detailedProperty"],
        factory_structure = data["factoryStructure"],
        eia = data["eia"],
        office_name = data["officeName"],
        address_region = ",".join(data["address"]["region"]) if data["address"]["region"] != "" else ",",
        address_detail = data["address"]['detail'],
        business_status = data["businessStatus"],
        area_building = float(data["area"]["buildingArea"]) if data["area"]["buildingArea"] != "" else 0,
        area_usable = float(data["area"]["usableArea"]) if data["area"]["usableArea"] != "" else 0,
        floor = data["floor"]["selectedIndex"],
        floor_data = data["floor"]["data"]["total"] + "," + data["floor"]["data"]["number"] + "," + data["floor"]["data"]["where"] + ",".join(data["firstFloor"].values()),
        decoration = data["decoration"],
        ownership = data["ownership"],
        rent_price = float(data["rentPrice"]) if data["rentPrice"] != "" else 0,
        min_lease_term = int(data["minLeaseTerm"]) if data["minLeaseTerm"] != "" else 0,

        sale_price = float(data["salePrice"]) if data["salePrice"] != "" else 0,
        home_owner = data["homeOwner"]["name"] + "," + data["homeOwner"]["phone"],
        notes = data["notes"],
        images = json.dumps(data["images"]),
        videos = json.dumps(data["videos"]),
        group = services.group.get(data["groupId"]),
        owner = services.user.get(int(data["ownerId"])),
        raw = json.dumps(data, ensure_ascii = False),
    )
    db.session.add(house)
    db.session.commit()
    return house

def get_onsale(user: Union[int, User]) -> list:
    if type(user) == int:
        user = services.user.get(user)

    if user is None:
        houses = []
    elif user.supervisor:
        houses = House.query.filter(House.transaction_type == 1, House.removed == False).all()
    elif services.user.is_administrator(user):
        groups = [group['id'] for group in services.user.group_manageable(user)]
        houses = House.query.filter(House.transaction_type == 1, House.removed == False, House.group_id in groups)
    elif len(user.groups) != 0:
        houses = House.query.filter(House.transaction_type == 1, House.removed == False, House.owner_id == user.id)
    else:
        houses = []
    return houses

def get_onrent(user: Union[int, User]) -> list:
    if type(user) == int:
        user = services.user.get(user)

    if user is None:
        houses = []
    elif user.supervisor:
        houses = House.query.filter(House.transaction_type == 2, House.removed == False).all()
    elif services.user.is_administrator(user):
        groups = [group['id'] for group in services.user.group_manageable(user)]
        houses = House.query.filter(House.transaction_type == 2, House.removed == False, House.group_id in groups)
    elif len(user.groups) != 0:
        houses = House.query.filter(House.transaction_type == 2, House.removed == False, House.owner_id == user.id)
    else:
        houses = []
    return houses

def get_removed(user: Union[int, User]) -> list:
    if type(user) == int:
        user = services.user.get(user)

    if user is None:
        houses = []
    elif user.supervisor:
        houses = House.query.filter(House.removed == True).all()
    elif services.user.is_administrator(user):
        groups = [group['id'] for group in services.user.group_manageable(user)]
        houses = House.query.filter(House.removed == True, House.group_id in groups)
    elif len(user.groups) != 0:
        houses = House.query.filter(House.removed == True, House.owner_id == user.id)
    else:
        houses = []
    return houses

def remove(house: Union[int, House]):
    if type(house) == int:
        house: House = get(house)
    house.removed = True
    db.session.commit()
    return

def listing(house: Union[int, House]):
    if type(house) == int:
        house: House = get(house)
    house.removed = False
    db.session.commit()
    return

def raw(house: Union[int, House]):
    if type(house) == int:
        house: House  = get(house)
    return json.loads(house.raw)

def update(data: dict, uid: int) -> House:
    house = get(int(data["id"]))
    house.title = data["title"]
    house.house_type = data["houseType"]
    house.transaction_type = data["transactionType"]
    house.transfer_type = data["transferType"]
    house.rent_type = data["rentType"]
    house.property = data["property"]
    house.detailed_property = data["detailedProperty"]
    house.factory_structure = data["factoryStructure"]
    house.eia = data["eia"]
    house.office_name = data["officeName"]
    house.address_region = ",".join(data["address"]["region"]) if data["address"]["region"] != "" else ","
    house.address_detail = data["address"]['detail']
    house.business_status = data["businessStatus"]
    house.area_building = float(data["area"]["buildingArea"]) if data["area"]["buildingArea"] != "" else 0
    house.area_usable = float(data["area"]["usableArea"]) if data["area"]["usableArea"] != "" else 0
    house.floor = data["floor"]["selectedIndex"]
    house.floor_data = data["floor"]["data"]["total"] + "," + data["floor"]["data"]["number"] + "," + data["floor"]["data"]["where"] + ",".join(data["firstFloor"].values())
    house.decoration = data["decoration"]
    house.ownership = data["ownership"]
    house.rent_price = float(data["rentPrice"]) if data["rentPrice"] != "" else 0
    house.min_lease_term = int(data["minLeaseTerm"]) if data["minLeaseTerm"] != "" else 0

    house.sale_price = float(data["salePrice"]) if data["salePrice"] != "" else 0
    house.home_owner = data["homeOwner"]["name"] + "," + data["homeOwner"]["phone"]
    house.notes = data["notes"]
    house.images = json.dumps(data["images"])
    house.videos = json.dumps(data["videos"])
    if house.group_id != data["groupId"]:
        house.group = services.group.get(data["groupId"])
        house.owner = services.user.get(int(data["ownerId"]) if data["ownerId"] != "" else uid)
    elif house.owner_id != int(data["ownerId"]):
        house.owner = services.user.get(int(data["ownerId"]) if data["ownerId"] != "" else uid)
    house.raw = json.dumps(data, ensure_ascii = False)
    db.session.commit()
    return house

def change_owner(house: Union[int, House], owner: Union[int, User]):
    if type(house) == int:
        house: House = get(house)
    if type(owner) == int:
        owner: User = services.user.get(owner)

    if house.owner_id != owner.id:
        house.owner = owner
        raw = json.loads(house.raw)
        raw["ownerId"] = str(owner.id)
        house.raw = json.dumps(raw)
        db.session.commit()
    return

def recommend(house_type: int = 0, numbers: int = 10) -> list:
    if house_type == 0:
        houses = House.query.filter(House.reference_id != None, House.removed == False).order_by(House.id.desc()).limit(numbers).all()
    else:
        houses = House.query.filter(House.reference_id != None, House.house_type == house_type, House.removed == False).order_by(House.id.desc()).limit(numbers).all()
    return houses

def latest(house_type: int = 0, numbers: int = 20) -> list:
    if house_type == 0:
        houses = House.query.filter(House.removed == False).order_by(House.id.desc()).limit(numbers).all()
    else:
        houses = House.query.filter(House.house_type == house_type, House.removed == False).order_by(House.id.desc()).limit(numbers).all()
    return houses

def search(
        keyword: str = "",
        region: str = "",
        house_type: int = 0,
        transaction_type: int = 0,
        area_min: int = 0,
        area_max: int = 0,
        price_min: int = 0,
        price_max: int = 0,
        offset: int = 0,
        number: int = 20,
        **kwargs
):
    houses = House.query.filter(House.removed == False)

    if keyword != "":
        houses = houses.filter(or_(
            House.title.like(f"%{keyword}%"),
            House.office_name.like(f"%{keyword}%")
        ))

    # 房屋区域
    if type(region) == str:
        # 兼容旧版参数
        if region != "":
            region = region.replace(",不限", "")
            houses = houses.filter(House.address_region.like(f"%{region}%"))
    elif type(region) == list:
        # 新版参数
        if "不限" in region[-1] or len(region[-1]) == 0:
            # 参数包含"不限"则移除末级所有选项，防止前端接口末级参数错误造成的搜索错误。
            region.pop()
        if len(region) > 0:
            if type(region[-1]) == str:
                # 为实现末项多选，应保证参数最后一项为列表。
                region[-1] = [region[-1]]
            houses = houses.filter(or_(*[House.address_region.like(f"%{item}%") for item in region[-1]]))

    # 房屋类型
    if house_type != 0:
        houses = houses.filter(House.house_type == house_type)
    # 租售类型
    if transaction_type != 0:
        houses = houses.filter(House.transaction_type == transaction_type)
    # 房屋面积
    if area_min != 0:
        houses = houses.filter(or_(
            House.area_usable >= area_min,
            House.area_building >= area_min
        ))
    if area_max != 0 and area_max != area_min:
        houses = houses.filter(or_(
            House.area_usable <= area_max,
            House.area_building <= area_max
        ))
    # 房屋价格
    if transaction_type == 1:  # 出售
        if price_min != 0:
            houses = houses.filter(House.sale_price >= price_min)
        if price_max != 0 and price_max != price_min:
            houses = houses.filter(House.sale_price <= price_max)
    elif transaction_type == 2:  # 出租
        if price_min != 0:
            houses = houses.filter(House.rent_price >= price_min)
        if price_max != 0 and price_max != price_min:
            houses = houses.filter(House.rent_price <= price_max)
    else:
        # if price_min != 0:
        #     houses = houses.filter(
        #         or_(
        #             and_(House.transaction_type == 1, House.sale_price >= price_min),
        #             and_(House.transaction_type == 2, House.rent_price >= price_min),
        #         )
        #     )
        # if price_max != 0 and price_max != price_min:
        #     houses = houses.filter(
        #         or_(
        #             and_(House.transaction_type == 1, House.sale_price <= price_max),
        #             and_(House.transaction_type == 2, House.rent_price <= price_max),
        #         )
        #     )
        pass  # 全部类型时价格区间无效。
    if offset == 0:
        total = houses
        total_num = len(total.all())
    else:
        total_num = -1
    return houses.offset(offset).limit(number).all(), total_num

def detail(house: Union[int, House], user: Union[int, User]):
    if type(house) == int:
        house: House = get(house)
    if type(user) == int:
        user: User = services.user.get(user)

    if house.removed:
        raw = []
    else:
        raw = json.loads(house.raw)
        raw["address"].pop("required")
        raw["area"].pop("required")
        raw["floor"].pop("required")
        raw.pop("homeOwner")
        if user is None:
            raw["hearted"] = 0
            raw["recommended"] = 0
            raw["owner"] = ""
        else:
            raw["hearted"] = 1 if house.id in [collention.id for collention in user.collections] else 2
            if user.supervisor or services.user.is_administrator(user) or house.owner_id == user.id:
                raw["recommended"] = 1 if house.reference_id == user.id else 2
            else:
                raw["recommended"] = 0

            if user.supervisor or house.group_id in [group.id for group in user.groups]:
                owner = services.user.get(house.owner_id)
                group = services.group.get(house.group_id)
                raw["owner"] = f"{group.name} - {owner.nickname}"
            else:
                raw["owner"] = ""
    return raw


