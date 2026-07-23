"""
分类模块 API
- GET    /api/v1/categories          分类列表
- POST   /api/v1/categories          新建分类（需登录）
- PUT    /api/v1/categories/<id>     更新分类（需登录）
- DELETE /api/v1/categories/<id>     删除分类（需登录）
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.models import db, Category, Article
from app.utils.responses import (
    success_response,
    error_response,
    paginate_response,
)

category_bp = Blueprint('category', __name__)


@category_bp.route('/categories', methods=['GET'])
def list_categories():
    include_count = request.args.get('include_count') == 'true'
    q = Category.query.order_by(Category.created_at.asc())

    items = []
    for c in q.all():
        d = c.to_dict()
        if include_count:
            d['article_count'] = Article.query.filter(
                Article.categories.any(Category.id == c.id)
            ).count()
        items.append(d)

    return success_response(items)


@category_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return error_response('名称不能为空', 400)

    if Category.query.filter_by(name=name).first():
        return error_response('分类已存在', 400)

    cat = Category(name=name)
    db.session.add(cat)
    db.session.commit()

    return success_response(cat.to_dict(), message='创建成功', code=201)


@category_bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id: int):
    cat = Category.query.get(category_id)
    if not cat:
        return error_response('分类不存在', 404)

    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return error_response('名称不能为空', 400)

    existing = Category.query.filter_by(name=name).first()
    if existing and existing.id != cat.id:
        return error_response('名称已被使用', 400)

    cat.name = name
    db.session.commit()

    return success_response(cat.to_dict(), message='更新成功')


@category_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id: int):
    cat = Category.query.get(category_id)
    if not cat:
        return error_response('分类不存在', 404)

    db.session.delete(cat)
    db.session.commit()
    return success_response(message='删除成功')


@category_bp.route('/categories/batch', methods=['POST'])
@jwt_required()
def batch_delete_categories():
    data = request.get_json() or {}
    ids = data.get('ids') or []
    if not ids:
        return error_response('请选择要删除的分类', 400)
    Category.query.filter(Category.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    return success_response(message=f'已删除 {len(ids)} 个分类')
