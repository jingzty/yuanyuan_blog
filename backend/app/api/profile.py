"""
博主资料 API
- GET  /api/v1/profile     获取资料
- PUT  /api/v1/profile     更新资料（需登录）
"""

import json
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.models import db, Profile
from app.utils.responses import success_response, error_response

profile_bp = Blueprint('profile', __name__)


def _get_or_create_profile() -> Profile:
    p = Profile.query.get(1)
    if not p:
        p = Profile(
            id=1,
            nickname='远远',
            bio='你好，我是远远。\n一个热爱旅行、摄影和写作的人。在这里记录生活中的每一个值得被记住的瞬间。',
            social_links=json.dumps([
                {'name': 'github', 'url': 'https://github.com', 'icon': 'github'},
                {'name': 'twitter', 'url': 'https://twitter.com', 'icon': 'twitter'},
            ]),
        )
        db.session.add(p)
        db.session.commit()
    return p


@profile_bp.route('/profile', methods=['GET'])
def get_profile():
    return success_response(_get_or_create_profile().to_dict())


@profile_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    p = _get_or_create_profile()
    data = request.get_json() or {}

    if 'avatar_url' in data:
        p.avatar_url = data['avatar_url']
    if 'nickname' in data:
        p.nickname = (data['nickname'] or '').strip()
    if 'bio' in data:
        p.bio = data['bio']
    if 'social_links' in data:
        p.social_links = json.dumps(data['social_links'], ensure_ascii=False)

    db.session.commit()
    return success_response(p.to_dict(), message='保存成功')