from datetime import datetime
from flask import render_template, request
from run import app
from mingqiang.model import Counters
from mingqiang.response import make_succ_empty_response, make_succ_response, make_err_response


@app.route('/')
def index():
    # return render_template('index.html')
    return make_err_response("Invalid URL.")

@app.route('/api/test', methods=['POST'])
def count():
    """
    :return:上传的数据
    """

    # 获取请求体参数
    params = request.get_json()

    return make_succ_response(params)

@app.route('/api/search', methods=['POST'])
def search_house():
    """
    :return: 符合条件的房源信息
    """

    return make_succ_response(["123", "345"])