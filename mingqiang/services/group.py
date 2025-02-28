from mingqiang.model import User, Group, House, UserGroupShip
from mingqiang import db, app, house_id_generator, user_id_generator
from mingqiang import services
from typing import Union


def get(id: int) -> Union[Group, None]:
    group = Group.query.get(id)
    return group

def get_all() -> list:
    groups = Group.query.all()
    return groups

def is_administrator(user: int|User, group: int|Group) -> bool:
    if type(user) == int:
        user: User = services.user.get(user)
    if type(group) == int:
        group: Group = get(group)

    ugship: UserGroupShip = UserGroupShip.query.filter(User.id == user.id, Group.id == group.id).first()
    role = ugship.role
    return (role == 1 or role == 2)

def response(group: Union[int, Group]) -> dict:
    if type(group) == int:
        group: Group = get(group)
    res = {
        "id": group.id,
        "name": group.name,
    }
    return res

def get_creator(group: Union[int, Group]) -> Union[User, None]:
    if type(group) == int:
        group: Group = get(group)
    
    creators = UserGroupShip.query.filter(UserGroupShip.role == 2).all()
    creators = [creator.user_id for creator in creators]
    if len(creators) > 0:
        return services.user.get(creators[0])
    else:
        return None

