"""
文章推荐模块 API
- GET    /api/v1/featured       列表（前台只取 enabled 且文章已发布；后台可传 status）
- POST   /api/v1/featured       新建（需登录）
- PUT    /api/v1/featured/<id>  更新（需登录）
- DELETE /api/v1/featured/<id>  删除（需登录）
- GET    /api/v1/featured/stats 统计
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.models import db, FeaturedArticle, Article
from app.utils.responses import (
    success_response,
    error_response,
)

featured_bp = Blueprint('featured', __name__)


@featured_bp.route('/featured', methods=['GET'])
def list_featured():
    status = request.args.get('status')
    q = FeaturedArticle.query
    if status:
        q = q.filter(FeaturedArticle.status == status)
    q = q.order_by(FeaturedArticle.sort_order.asc(), FeaturedArticle.created_at.desc())

    items = []
    for f in q.all():
        # 关联文章被删除则跳过
        if not f.article:
            continue
        items.append(f.to_dict())
    return success_response(items)


@featured_bp.route('/featured', methods=['POST'])
@jwt_required()
def create_featured():
    data = request.get_json() or {}
    article_id = data.get('article_id')
    sort_order = int(data.get('sort_order', 0) or 0)
    status = data.get('status') or 'enabled'

    if not article_id:
        return error_response('请选择文章', 400)
    article = Article.query.get(article_id)
    if not article:
        return error_response('文章不存在', 400)
    if status not in ('enabled', 'disabled'):
        return error_response('状态非法', 400)

    existing = FeaturedArticle.query.filter_by(article_id=article_id).first()
    if existing:
        return error_response('该文章已在推荐列表中', 400)

    f = FeaturedArticle(
        article_id=article_id,
        sort_order=sort_order,
        status=status,
    )
    db.session.add(f)
    db.session.commit()

    return success_response(f.to_dict(), message='创建成功', code=201)


@featured_bp.route('/featured/<int:featured_id>', methods=['PUT'])
@jwt_required()
def update_featured(featured_id: int):
    f = FeaturedArticle.query.get(featured_id)
    if not f:
        return error_response('推荐项不存在', 404)

    data = request.get_json() or {}
    if 'article_id' in data and data['article_id']:
        new_id = data['article_id']
        if new_id != f.article_id:
            if not Article.query.get(new_id):
                return error_response('文章不存在', 400)
            if FeaturedArticle.query.filter_by(article_id=new_id).first():
                return error_response('该文章已在推荐列表中', 400)
            f.article_id = new_id
    if 'sort_order' in data:
        f.sort_order = int(data['sort_order'] or 0)
    if 'status' in data:
        if data['status'] not in ('enabled', 'disabled'):
            return error_response('状态非法', 400)
        f.status = data['status']

    db.session.commit()
    return success_response(f.to_dict(), message='更新成功')


@featured_bp.route('/featured/<int:featured_id>', methods=['DELETE'])
@jwt_required()
def delete_featured(featured_id: int):
    f = FeaturedArticle.query.get(featured_id)
    if not f:
        return error_response('推荐项不存在', 404)
    db.session.delete(f)
    db.session.commit()
    return success_response(message='删除成功')


@featured_bp.route('/featured/stats', methods=['GET'])
@jwt_required()
def featured_stats():
    from sqlalchemy import func
    total = db.session.query(func.count(FeaturedArticle.id)).scalar() or 0
    enabled = db.session.query(func.count(FeaturedArticle.id)).filter(
        FeaturedArticle.status == 'enabled'
    ).scalar() or 0
    disabled = db.session.query(func.count(FeaturedArticle.id)).filter(
        FeaturedArticle.status == 'disabled'
    ).scalar() or 0
    return success_response({
        'total': total,
        'enabled': enabled,
        'disabled': disabled,
    })
