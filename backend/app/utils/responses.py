"""
统一响应工具
"""

from flask import jsonify


def success_response(data=None, message: str = 'success', code: int = 200):
    """成功响应"""
    resp = {
        'code': code,
        'message': message,
        'data': data,
    }
    return jsonify(resp), code


def error_response(message: str = 'error', code: int = 400, data=None):
    """错误响应"""
    resp = {
        'code': code,
        'message': message,
        'data': data,
    }
    return jsonify(resp), code


def paginate_response(query, page: int, per_page: int, serializer=None):
    """分页响应封装"""
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items

    if serializer:
        items = [serializer(item) for item in items]

    data = {
        'items': items,
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
        'has_prev': pagination.has_prev,
        'has_next': pagination.has_next,
    }
    return success_response(data)
