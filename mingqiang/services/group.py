from mingqiang.model import User, Group, House
from mingqiang import db, app, house_id_generator, user_id_generator
from typing import Union


def get(id: int) -> Union[Group, None]:
    group = Group.query.get(id)
    return group

def get_all() -> list:
    groups = Group.query.all()
    return groups

def response(group: Union[int, Group]) -> dict:
    if type(group) == int:
        group: Group = get(group)
    res = {
        "id": group.id,
        "name": group.name,
    }
    return res

