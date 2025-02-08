from mingqiang.model import User, Group, House, UserGroupShip, UserCollectionShip
from mingqiang import db, app, house_id_generator, user_id_generator
from mingqiang import services
from typing import Union


def find_with_openid(openid) -> Union[User, None]:
    user = User.query.filter(User.openid == openid).first()
    return user

def get(id: int) -> Union[User, None]:
    user = User.query.get(id)
    return user

def get_all() -> list:
    users = User.query.all()
    return users

def new(openid: str) -> User:
    new_user = User(id = user_id_generator.generate(), openid = openid)
    db.session.add(new_user)
    db.session.commit()
    return new_user

def response(user: Union[int, User]) -> dict:
    if type(user) == int:
        user: User = get(user)
    res = {
        "id": str(user.id), 
        "nickname": user.nickname, 
        "avatar": user.avatar, 
        "supervisor": user.supervisor,
        "administrator": is_administrator(user),
        "groups": [{"id": group.id, "name": group.name} for group in user.groups],
        "houses": [{"id": str(house.id)} for house in user.houses],
    }
    return res

def group_in(user: Union[int, User], group: Union[int, Group]) -> bool:
    if type(user) == int:
        user: User = get(user)
    if type(group) == Group:
        group: int = group.id
    group_ids = [group.id for group in user.groups]
    return group in group_ids

def group_join(user: Union[int, User], group: Union[int, Group]):
    """
    函数内不进行校验，函数外务必校验参数是否合法。
    """
    if type(user) == int:
        user: User = get(user)
    if type(group) == int:
        group: Group = group.id
    group.members.append(user)
    db.session.commit()
    return

def group_remove(user: Union[int, User], group: Union[int, Group]):
    if type(user) == int:
        user: User = get(user)
    if type(group) == int:
        group: Group = group
    UserGroupShip.query.filter_by(user_id = user.id, group_id = group.id).delete()
    db.session.commit()
    return

def group_manageable(user: Union[int, User]) -> list:
    if type(user) == int:
        user: User = get(user)
    if user.supervisor:
        # 超级管理员可管理所有组
        result = [{"id": group.id, "name": group.name} for group in services.group.get_all()]
    else:
        result = [{"id": group.id, "name": group.name} for group in user.groups if group.role > 0]
    return result

def get_role(user: Union[int, User], group: Union[int, Group]) -> int:
    if type(user) == User:
        user: int = user.id
    if type(group) == Group:
        group: int = group.id
    ugship = UserGroupShip.query.filter_by(user_id = user, group_id = group).first()
    return ugship.role

def update(user: Union[int, User], openid: str = None, nickname: str = None, avatar: str = None, supervisor: bool = None, group_id: int = None, role: int = None):
    if type(user) == int:
        user: User = get(user)
    if user:
        if openid is not None:
            user.openid = openid
        if nickname is not None:
            user.nickname = nickname
        if avatar is not None:
            user.avatar = avatar
        if supervisor is not None:
            user.supervisor = supervisor
        if group_id is not None and role is not None:
            update_role(id, group_id, role)
        db.session.commit()
    return user

def is_administrator(user: Union[int, User]) -> bool:
    if type(user) == int:
        user: User = get(user)
    roles = []
    for group in user.groups:
        ugship = UserGroupShip.query.filter_by(user_id = user.id, group_id = group.id).first()
        roles.append(ugship.role)
    return any([role == 1 or role == 2 for role in roles])

def update_role(user: Union[int, User], group: Union[int, Group], role: int):
    if type(user) == int:
        user: User = get(user)
    if type(group) == int:
        group: Group = get(user)
    if get_role(user, group) is not None:  # 用户在用户组中
        ugship = UserGroupShip.query.filter_by(user_id = user.id, group_id = group.id).first()
        ugship.role = role
        db.session.commit()
    return

def heart(user: Union[int, User], house: Union[int, House]) -> bool:
    if type(user) == int:
        user: User = get(user)
    if type(house) == int:
        house: House = services.house.get(house)
    collentions = [collention.id for collention in user.collections]
    if house.id in collentions:
        return False
    user.collections.append(house)
    db.session.commit()
    return True

def cancel_heart(user: Union[int, User], house: Union[int, House]) -> bool:
    if type(user) == int:
        user: User = get(user)
    if type(house) == int:
        house: House = services.house.get(house)
    collentions = [collention.id for collention in user.collections]
    if house.id not in collentions:
        return False
    UserCollectionShip.query.filter_by(user_id = user.id, house_id = house.id).delete()
    db.session.commit()
    return True

def heart_list(user: Union[int, User]):
    if type(user) == int:
        user: User = get(user)
    houses = user.collections
    houses = [house for house in houses if house.removed is False]
    return houses

