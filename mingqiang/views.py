from flask import render_template, request, jsonify
from mingqiang import app, map
import json
import random

from mingqiang import services

# @app.route("/", methods = ["GET"])
# def index():
#     return jsonify({}), 200

@app.route("/api/login", methods = ["GET"])
def login():
    # 获取openid和session_key
    openid = request.headers["X-Wx-Openid"]

    with app.app_context():
        try:
            user = services.user.find_with_openid(openid)
            if user is None:
                user = services.user.new(openid = openid)
                code = 201
            else:
                # user = services.user.update(user)
                code = 200
        except Exception as e:
            app.logger.warning(e)

        return jsonify({"status": "success", "openid": openid, "user": services.user.response(user)}), code

@app.route("/api/user/info", methods = ["GET", "POST"])
def user_info():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if not request.data:
            user_id = None
        else:
            user_id = request.get_json().get("userId", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无查询权限"}
        elif user_id is None:
            # 获取当前用户信息
            user = services.user.get(int(uid))
            response = {"status": "success", "user": services.user.response(user)}
        else:
            # 获取指定用户信息，需要管理员权限
            user_ = services.user.get(int(uid))
            if user_.supervisor or services.user.is_administrator(user_):
                user = services.user.get(int(user_id))
                response = {"status": "success", "user": services.user.response(user)}
            else:
                response = {"status": "error", "errorMsg": "无查询权限"}
        return jsonify(response), 200

@app.route("/api/user/update/avatar", methods = ["POST"])
def user_update_avatar():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not request.data:
            response = {"status": "error", "errorMsg":"缺少参数:avatar"}
        else:
            avatar = request.get_json().get("avatar", None)
            if avatar is None:
                response = {"status": "error", "errorMsg":"缺少参数:avatar"}
            else:
                services.user.update(int(uid), avatar = avatar)
                response = {"status": "success"}
        return jsonify(response), 200

@app.route("/api/user/update/nickname", methods = ["POST"])
def user_update_nickname():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not request.data:
            response = {"status": "error", "errorMsg":"缺少参数:nickname"}
        else:
            nickname = request.get_json().get("nickname", None)
            if nickname is None:
                response = {"status": "error", "errorMsg":"缺少参数:nickname"}
            else:
                services.user.update(int(uid), nickname = nickname)
                response = {"status": "success"}
        return jsonify(response), 200

@app.route("/api/user/heartList", methods = ["GET"])
def user_heart_list():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "Uid错误"}
        else:
            houses = services.user.heart_list(int(uid))
            houses = [{
                "id": str(house.id),
                "cover": json.loads(house.images)[0]["filePath"],
                "title": house.title,
                "area": str(house.area_building),
                "region": house.address_region.split(",")[3],
                "price": f"{house.sale_price}万元" if house.transaction_type == 1 else f"{house.rent_price}万元/月",
                "transaction_type": house.transaction_type,
            } for house in houses]
            response = {"status": "success", "houses": houses}
        return jsonify(response), 200

@app.route("/api/user/recommendList", methods = ["GET"])
def user_recommend_list():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "Uid错误"}
        else:
            # houses = services.user.recommend_list(int(uid))
            houses = services.user.heart_list(int(uid))
            houses = [{
                "id": str(house.id),
                "cover": json.loads(house.images)[0]["filePath"],
                "title": house.title,
                "area": str(house.area_building),
                "region": house.address_region.split(",")[3],
                "price": f"{house.sale_price}万元" if house.transaction_type == 1 else f"{house.rent_price}万元/月",
                "transaction_type": house.transaction_type,
            } for house in houses]
            response = {"status": "success", "houses": houses}
        return jsonify(response), 200


# 未完成
@app.route("/api/user/all", methods = ["GET", "POST"])
def user_all():
    with app.app_context():
        response = {"status": "error", "errorMsg": "未开放接口"}
        return jsonify(response), 200



# 未完成
@app.route("/api/house/detail/<house_id>", methods = ["GET"])
def house_detail(house_id):
    with app.app_context():
        uid = request.headers.get("Uid", None)
        house = services.house.get(int(house_id))
        if house is None:
            response = {"status": "error", "errorMsg": "Id无效"}
        else:
            detail = services.house.detail(house, int(uid))
            response = {"status": "success", "detail": detail}
        
        return jsonify(response), 200

@app.route("/api/house/newid", methods = ["GET"])
def house_newid():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not services.user.get(int(uid)).supervisor and len(services.user.get(int(uid)).groups) == 0:
            response = {"status": "error", "errorMsg": "无操作权限"}
        else:
            house_id = services.house.new_id()
            response = {"status": "success", "id": str(house_id)}
        return jsonify(response), 200

@app.route("/api/house/new", methods = ["POST"])
def house_new():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not services.user.get(int(uid)).supervisor and len(services.user.get(int(uid)).groups) == 0:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not request.data:
            response = {"status": "error", "errorMsg": "缺少参数"}
        else:
            data = request.get_json()
            services.house.new(data)
            response = {"status": "success"}
        return jsonify(response), 200
    
@app.route("/api/house/onsale", methods = ["GET"])
def house_onsale():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无查询权限"}
        elif not services.user.is_administrator(int(uid)) and not services.user.get(int(uid)).supervisor and len(services.user.get(int(uid)).groups) == 0:
            response = {"status": "error", "errorMsg": "无查询权限"}
        else:
            houses = services.house.get_onsale(int(uid))
            houses = [{
                "id": str(house.id),
                "cover": json.loads(house.images)[0]["filePath"],
                "title": house.title,
                "area": str(house.area_building),
                "region": house.address_region.split(",")[3],
                "price": f"{house.sale_price}万元",
                "transaction_type": house.transaction_type,
            } for house in houses]
            response = {"status": "success", "houses": houses}
        return jsonify(response), 200

@app.route("/api/house/onrent", methods = ["GET"])
def house_onrent():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无查询权限"}
        elif not services.user.is_administrator(int(uid)) and not services.user.get(int(uid)).supervisor and len(services.user.get(int(uid)).groups) == 0:
            response = {"status": "error", "errorMsg": "无查询权限"}
        else:
            houses = services.house.get_onrent(int(uid))
            houses = [{
                "id": str(house.id),
                "cover": json.loads(house.images)[0]["filePath"],
                "title": house.title,
                "area": str(house.area_building),
                "region": house.address_region.split(",")[3],
                "price": f"{house.rent_price}万元/月",
                "transaction_type": house.transaction_type,
            } for house in houses]
            response = {"status": "success", "houses": houses}
        return jsonify(response), 200

@app.route("/api/house/removed", methods = ["GET"])
def house_removed():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无查询权限"}
        elif not services.user.is_administrator(int(uid)) and not services.user.get(int(uid)).supervisor and len(services.user.get(int(uid)).groups) == 0:
            response = {"status": "error", "errorMsg": "无查询权限"}
        else:
            houses = services.house.get_removed(int(uid))
            houses = [{
                "id": str(house.id),
                "cover": json.loads(house.images)[0]["filePath"],
                "title": house.title,
                "area": str(house.area_building),
                "region": house.address_region.split(",")[3],
                "price": f"{house.sale_price}万元" if house.transaction_type == 1 else f"{house.rent_price}万元/月",
                "transaction_type": house.transaction_type,
            } for house in houses]
            response = {"status": "success", "houses": houses}
        return jsonify(response), 200

@app.route("/api/house/remove", methods = ["POST"])
def house_remove():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not services.user.is_administrator(int(uid)) and not services.user.get(int(uid)).supervisor and len(services.user.get(int(uid)).groups) == 0:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not request.data:
            response = {"status": "error", "errorMsg":"缺少参数:houseId"}
        else:
            house_id = request.get_json().get("houseId", None)
            if house_id is None:
                response = {"status": "error", "errorMsg": "缺少参数:houseId"}
            else:
                services.house.remove(int(house_id))
                response = {"status": "success"}
        return jsonify(response), 200

@app.route("/api/house/listing", methods = ["POST"])
def house_listing():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无查询权限"}
        elif not services.user.is_administrator(int(uid)) and not services.user.get(int(uid)).supervisor:
            response = {"status": "error", "errorMsg": "无查询权限"}
        elif not request.data:
            response = {"status": "error", "errorMsg":"缺少参数:houseId"}
        else:
            house_id = request.get_json().get("houseId", None)
            if house_id is None:
                response = {"status": "error", "errorMsg": "缺少参数:houseId"}
            else:
                services.house.listing(int(house_id))
                response = {"status": "success"}
        return jsonify(response), 200

@app.route("/api/house/raw", methods = ["POST"])
def house_raw():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无查询权限"}
        elif not services.user.is_administrator(int(uid)) and not services.user.get(int(uid)).supervisor and len(services.user.get(int(uid)).groups) == 0:
            response = {"status": "error", "errorMsg": "无查询权限"}
        elif not request.data:
            response = {"status": "error", "errorMsg":"缺少参数:houseId"}
        else:
            house_id = request.get_json().get("houseId", None)
            if house_id is None:
                response = {"status": "error", "errorMsg": "缺少参数:houseId"}
            else:
                raw = services.house.raw(int(house_id))
                response = {"status": "success", "raw": raw}
        return jsonify(response), 200

@app.route("/api/house/update", methods = ["POST"])
def house_update():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not services.user.get(int(uid)).supervisor and len(services.user.get(int(uid)).groups) == 0:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not request.data:
            response = {"status": "error", "errorMsg": "缺少参数"}
        else:
            data = request.get_json()
            services.house.update(data, int(uid))
            response = {"status": "success"}

        return jsonify(response), 200

@app.route("/api/house/recommend", methods = ["POST"])
def house_recommend():
    with app.app_context():
        if not request.data:
            house_type = 0
        else:
            house_type = request.get_json().get("houseType", 0)
        houses = services.house.recommend(house_type, 20)
        houses = [{
            "id": str(house.id),
            "cover": json.loads(house.images)[0]["filePath"],
            "title": house.title,
            "area": str(house.area_building),
            "region": house.office_name if house.house_type == 2 else house.address_region.split(",")[3],
            "price": f"{house.sale_price}万元" if house.transaction_type == 1 else f"{house.rent_price}万元/月",
            "transaction_type": house.transaction_type,
        } for house in houses]
        random.shuffle(houses)
        response = {"status": "success", "houses": houses}
        return jsonify(response), 200
    
@app.route("/api/house/latest", methods = ["POST"])
def house_latest():
    with app.app_context():
        if not request.data:
            house_type = 0
        else:
            house_type = request.get_json().get("houseType", 0)
        houses = services.house.latest(house_type, 20)
        houses = [{
            "id": str(house.id),
            "cover": json.loads(house.images)[0]["filePath"],
            "title": house.title,
            "area": str(house.area_building),
            "region": house.office_name if (house.house_type == 2) else house.address_region.split(",")[3],
            "price": f"{house.sale_price}万元" if house.transaction_type == 1 else f"{house.rent_price}万元/月",
            "transaction_type": house.transaction_type,
        } for house in houses]
        response = {"status": "success", "houses": houses}
        return jsonify(response), 200

@app.route("/api/house/search", methods = ["POST"])
def house_search():
    with app.app_context():
        if not request.data:
            option = {}
        else:
            option = request.get_json().get("option", {})
        try:
            houses = services.house.search(**option)
            houses = [{
                "id": str(house.id),
                "cover": json.loads(house.images)[0]["filePath"],
                "title": house.title,
                "area": str(house.area_building),
                "region": house.office_name if (house.house_type == 2) else house.address_region.split(",")[3],
                "price": f"{house.sale_price}万元" if house.transaction_type == 1 else f"{house.rent_price}万元/月",
                "transaction_type": house.transaction_type,
            } for house in houses]
        except Exception as e:
            houses = []
        response = {"status": "success", "houses": houses}
        return jsonify(response), 200

@app.route("/api/house/heart", methods = ["POST"])
def house_heart():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "Uid错误"}
        elif not request.data:
            response = {"status": "error", "errorMsg":"缺少参数:houseId"}
        else:
            house_id = request.get_json().get("houseId", None)
            if house_id is None:
                response = {"status": "error", "errorMsg": "缺少参数:houseId"}
            else:
                result = services.user.heart(int(uid), int(house_id))
                response = {"status": "success"} if result else {"status": "error", "errorMsg": "重复收藏"}
        return jsonify(response), 200

@app.route("/api/house/cancelHeart", methods = ["POST"])
def house_cancel_heart():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "Uid错误"}
        elif not request.data:
            response = {"status": "error", "errorMsg":"缺少参数:houseId"}
        else:
            house_id = request.get_json().get("houseId", None)
            if house_id is None:
                response = {"status": "error", "errorMsg": "缺少参数:houseId"}
            else:
                result = services.user.cancel_heart(int(uid), int(house_id))
                response = {"status": "success"} if result else {"status": "error", "errorMsg": "无收藏记录"}
        return jsonify(response), 200




@app.route("/api/group/manageable", methods = ["GET"])
def group_manageable():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无查询权限"}
        elif not services.user.is_administrator(int(uid)) and not services.user.get(int(uid)).supervisor:
            response = {"status": "error", "errorMsg": "无查询权限"}
        else:
            groups = services.user.group_manageable(int(uid))
            response = {"status": "success", "groups": groups}
        return jsonify(response), 200

@app.route("/api/group/members", methods = ["POST"])
def group_members():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not services.user.is_administrator(int(uid)) and not services.user.get(int(uid)).supervisor:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not request.data:
            response = {"status": "error", "errorMsg": "缺少参数:groupId"}
        else:
            group_id = request.get_json().get("groupId", None)
            if group_id is None:
                response = {"status": "error", "errorMsg": "缺少参数:groupId"}
            else:
                group = services.group.get(group_id)
                if group is None:
                    response = {"status": "error", "errorMsg": "用户组不存在"}
                else:
                    members = group.members
                    members = [{"id":str(member.id), "nickname":member.nickname, "avatar":member.avatar, "role":services.user.get_role(member, group_id)} for member in members]
                    response = {"status": "success", "members": members}
        return jsonify(response), 200

@app.route("/api/group/add", methods = ["POST"])
def group_add():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not services.user.is_administrator(int(uid)) and not services.user.get(int(uid)).supervisor:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not request.data:
            response = {"status": "error", "errorMsg": "缺少参数"}
        else:
            user_id = request.get_json().get("userId", None)
            group_id = request.get_json().get("groupId", None)
            if user_id is None or group_id is None:
                response = {"status": "error", "errorMsg": "缺少参数"}
            else:
                user = services.user.get(int(user_id))
                group = services.group.get(int(group_id))
                if user is None:
                    response = {"status": "error", "errorMsg": "用户不存在"}
                elif group is None:
                    response = {"status": "error", "errorMsg": "用户组不存在"}
                elif services.user.group_in(user, group):
                    response = {"status": "error", "errorMsg": "用户已在分组中"}
                else:
                    services.user.group_join(user, group)
                    response = {"status": "success"}
        return jsonify(response), 200

# 暂无需求，未测试
@app.route("/api/group/update", methods = ["POST"])
def group_update():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not services.user.is_administrator(int(uid)) and not services.user.get(int(uid)).supervisor:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not request.data:
            response = {"status": "error", "errorMsg": "缺少参数"}
        else:
            user_id = request.get_json().get("userId", None)
            group_id = request.get_json().get("groupId", None)
            role = request.get_json().get("role", None)
            if user_id is None or group_id is None or role is None:
                response = {"status": "error", "errorMsg": "缺少参数"}
            else:
                user = services.user.get(int(user_id))
                group = services.group.get(int(group_id))
                if user is None:
                    response = {"status": "error", "errorMsg": "用户不存在"}
                elif group is None:
                    response = {"status": "error", "errorMsg": "用户组不存在"}
                elif role < 0 or role > 2:
                    response = {"status": "error", "errorMsg": "无效角色"}
                elif role == services.user.get_role(user, group):
                    response = {"status": "error", "errorMsg": "用户权限未变动"}
                else:
                    services.user.update_role(user, group, role)
                    response = {"status": "success"}
        return jsonify(response), 200

@app.route("/api/group/remove", methods = ["POST"])
def group_remove():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not services.user.is_administrator(int(uid)) and not services.user.get(int(uid)).supervisor:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not request.data:
            response = {"status": "error", "errorMsg": "缺少参数"}
        else:
            user_id = request.get_json().get("userId", None)
            group_id = request.get_json().get("groupId", None)
            if user_id is None or group_id is None:
                response = {"status": "error", "errorMsg": "缺少参数"}
            else:
                user = services.user.get(int(user_id))
                group = services.group.get(int(group_id))
                if user is None:
                    response = {"status": "error", "errorMsg": "用户不存在"}
                elif group is None:
                    response = {"status": "error", "errorMsg": "用户组不存在"}
                elif not services.user.group_in(user, group):
                    response = {"status": "error", "errorMsg": "用户未在分组中"}
                else:
                    services.user.group_remove(user, group)
                    response = {"status": "success"}
        return jsonify(response), 200

# 暂未完成
@app.route("/api/group/houses", methods = ["POST"])
def group_houses():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not services.user.is_administrator(int(uid)) and not services.user.get(int(uid)).supervisor:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not request.data:
            response = {"status": "error", "errorMsg": "缺少参数"}
        else:
            group_id = request.get_json().get("groupId", None)
            if group_id is None:
                response = {"status": "error", "errorMsg": "缺少参数"}
            else:
                group = services.group.get(int(group_id))
                if group is None:
                    response = {"status": "error", "errorMsg": "用户组不存在"}
                else:
                    houses = group.houses
                    houses = [{} for house in houses]
                    response = {"status": "success", "houses": houses}
        return jsonify(response), 200

# 手动添加，未设计
@app.route("/api/group/new", methods = ["POST"])
def group_new():
    
    return jsonify(), 200

@app.route("/api/group/delete", methods = ["POST"])
def group_delete():

    return jsonify(), 200

# 设计完成，未投入使用，未测试
# 此接口不用于用户组管理，用户组管理使用/api/group/manageable，保证接口一致性
@app.route("/api/group/all", methods = ["GET"])
def group_all():
    with app.app_context():
        uid = request.headers.get("Uid", None)
        if uid is None:
            response = {"status": "error", "errorMsg": "无操作权限"}
        elif not services.user.get(int(uid)).supervisor:
            response = {"status": "error", "errorMsg": "无操作权限"}
        else:
            groups = [services.group.response(group) for group in services.group.get_all()]
            response = {"status": "success", "groups": groups}
        return jsonify(response), 200

@app.route("/api/map/district/list", methods = ["GET"])
def map_district_list():
    if map.district_list == []:
        response = {"status": "error", "errorMsg": "无可用数据"}
    else:
        response = {"status": "success", "district": map.district_list}
    return jsonify(response), 200

@app.route("/api/map/district/children", methods = ["POST"])
def map_district_children():
    if not request.data:
        response = {"status": "error", "errorMsg": "缺少参数"}
    else:
        district_id = request.get_json().get("districtId", None)
        if district_id is None:
            response = {"status": "error", "errorMsg": "缺少参数"}
        else:
            result = map.map_district_get_children(id = district_id)
            if result == {}:
                response = {"status": "error", "errorMsg": "获取失败"}
            else:
                response = {"status": "success", "result": result}
    return jsonify(response), 200

@app.route("/api/map/geocoder", methods = ["POST"])
def map_geocoder():
    if not request.data:
        response = {"status": "error", "errorMsg": "缺少参数"}
    else:
        # latitude: 纬度
        # longitude: 经度
        latitude = request.get_json().get("latitude", None)
        longitude = request.get_json().get("longitude", None)
        if latitude is None or longitude is None:
            response = {"status": "error", "errorMsg": "缺少参数"}
        else:
            result = map.map_geocoder(latitude, longitude)
            if result["status"] == 0:
                response = {"status": "success", "result": result["result"]}
            else:
                response = {"status": "error", "errorMsg": result["message"]}
    return jsonify(response), 200