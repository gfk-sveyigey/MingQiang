from mingqiang.model import User, Group, House
from mingqiang import db, app, house_id_generator, user_id_generator
from mingqiang import services
from typing import Union
import json

def get(id: int) -> Union[House, None]:
    house = House.query.get(id)
    return house

def get_all() -> list:
    houses = House.query.all()
    return houses

def new(data: dict, uid: int) -> House:
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
        floor_data = data["floor"]["data"]["total"] + "," + data["floor"]["data"]["number"] + ",".join(data["firstFloor"].values()),
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
        owner = services.user.get(int(data["ownerId"]) if data["ownerId"] != "" else uid),
        raw = json.dumps(data, ensure_ascii = False),
    )
    db.session.add(house)
    db.session.commit()
    return house

def get_onsale() -> list:
    houses = House.query.filter(House.transaction_type == 1, House.removed == False).all()
    return houses

def get_onrent() -> list:
    houses = House.query.filter(House.transaction_type == 2, House.removed == False).all()
    return houses

def get_removed() -> list:
    houses = House.query.filter(House.removed == True).all()
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
    house.floor_data = data["floor"]["data"]["total"] + "," + data["floor"]["data"]["number"] + ",".join(data["firstFloor"].values())
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