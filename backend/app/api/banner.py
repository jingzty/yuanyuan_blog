"""
轮播图模块 API
- GET    /api/v1/banners     列表（前台可只取 enabled）
- POST   /api/v1/banners     新建（需登录）
- PUT    /api/v1/banners/<id> 更新（需登录）
- DELETE /api/v1/banners/<id> 删除（需登录）
- GET    /api/v1/banners/stats  统计
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.models import db, Banner
from app.utils.responses import (
    success_response,
    error_response,
)

banner_bp = Blueprint('banner', __name__)


@banner_bp.route('/banners', methods=['GET'])
def list_banners():
    status = request.args.get('status')
    q = Banner.query
    if status:
        q = q.filter(Banner.status == status)
    q = q.order_by(Banner.sort_order.asc(), Banner.created_at.desc())
    items = [b.to_dict() for b in q.all()]
    return success_response(items)


@banner_bp.route('/banners', methods=['POST'])
@jwt_required()
def create_banner():
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    subtitle = data.get('subtitle')
    image_url = data.get('image_url')
    link_url = data.get('link_url')
    sort_order = int(data.get('sort_order', 0) or 0)
    status = data.get('status') or 'enabled'

    if not title:
        return error_response('标题不能为空', 400)
    if not image_url:
        return error_response('图片 URL 不能为空', 400)
    if status not in ('enabled', 'disabled'):
        return error_response('状态非法', 400)

    banner = Banner(
        title=title,
        subtitle=subtitle,
        image_url=image_url,
        link_url=link_url,
        sort_order=sort_order,
        status=status,
    )
    db.session.add(banner)
    db.session.commit()

    return success_response(banner.to_dict(), message='创建成功', code=201)


@banner_bp.route('/banners/<int:banner_id>', methods=['PUT'])
@jwt_required()
def update_banner(banner_id: int):
    banner = Banner.query.get(banner_id)
    if not banner:
        return error_response('轮播图不存在', 404)

    data = request.get_json() or {}
    if 'title' in data:
        banner.title = (data['title'] or '').strip()
    if 'subtitle' in data:
        banner.subtitle = data['subtitle']
    if 'image_url' in data:
        banner.image_url = data['image_url']
    if 'link_url' in data:
        banner.link_url = data['link_url']
    if 'sort_order' in data:
        banner.sort_order = int(data['sort_order'] or 0)
    if 'status' in data:
        if data['status'] not in ('enabled', 'disabled'):
            return error_response('状态非法', 400)
        banner.status = data['status']

    db.session.commit()
    return success_response(banner.to_dict(), message='更新成功')


@banner_bp.route('/banners/<int:banner_id>', methods=['DELETE'])
@jwt_required()
def delete_banner(banner_id: int):
    banner = Banner.query.get(banner_id)
    if not banner:
        return error_response('轮播图不存在', 404)
    db.session.delete(banner)
    db.session.commit()
    return success_response(message='删除成功')


@banner_bp.route('/banners/stats', methods=['GET'])
@jwt_required()
def banner_stats():
    from sqlalchemy import func
    total = db.session.query(func.count(Banner.id)).scalar() or 0
    enabled = db.session.query(func.count(Banner.id)).filter(
        Banner.status == 'enabled'
    ).scalar() or 0
    disabled = db.session.query(func.count(Banner.id)).filter(
        Banner.status == 'disabled'
    ).scalar() or 0
    return success_response({
        'total': total,
        'enabled': enabled,
        'disabled': disabled,
    })
