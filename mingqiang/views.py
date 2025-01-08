from datetime import datetime
from flask import render_template, request
from run import app
from mingqiang.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from mingqiang.model import Counters
from mingqiang.response import make_succ_empty_response, make_succ_response, make_err_response


@app.route('/')
def index():
    # return render_template('index.html')
    return make_succ_response("名强房地产")


@app.route('/api/test', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    return make_succ_response(params)


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)


@app.route('/api/search', methods=['POST'])
def search_house():
    """
    :return: 符合条件的房源信息
    """

    return make_succ_response(["123", "345"])