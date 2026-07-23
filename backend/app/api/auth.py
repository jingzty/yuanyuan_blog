"""
认证模块 API
- POST /api/v1/auth/login     登录
- GET  /api/v1/auth/captcha   获取验证码
- GET  /api/v1/auth/me        当前用户信息
- POST /api/v1/auth/logout    登出
"""

import io
import random
import string
from datetime import datetime

from flask import Blueprint, request, session
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

from app.models import db, User
from app.utils.responses import success_response, error_response

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth/captcha', methods=['GET'])
def get_captcha():
    """生成简单文本验证码，返回 base64 PNG"""
    from PIL import Image, ImageDraw, ImageFont
    import base64

    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    session['captcha_code'] = code
    session['captcha_expires'] = datetime.utcnow().timestamp() + 300  # 5 分钟

    # 生成图片
    width, height = 120, 48
    img = Image.new('RGB', (width, height), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)

    # 尝试用系统字体，找不到就用默认
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    except Exception:
        font = ImageFont.load_default()

    # 干扰线
    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(200, 210, 220), width=1)

    # 字符
    for i, ch in enumerate(code):
        x = 15 + i * 25 + random.randint(-3, 3)
        y = 8 + random.randint(-3, 3)
        color = (
            random.randint(20, 80),
            random.randint(80, 150),
            random.randint(180, 240),
        )
        draw.text((x, y), ch, fill=color, font=font)

    # 输出 base64
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')

    return success_response({
        'captcha': f'data:image/png;base64,{b64}',
    })


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    captcha = (data.get('captcha') or '').strip().upper()

    # 1. 验证码校验
    expected = session.get('captcha_code', '').upper()
    expires = session.get('captcha_expires', 0)
    if not expected or datetime.utcnow().timestamp() > expires:
        return error_response('验证码已过期，请刷新', 401)
    if captcha != expected:
        return error_response('验证码错误', 401)

    # 2. 用户校验
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return error_response('用户名或密码错误', 401)

    # 3. 签发 JWT
    access_token = create_access_token(identity=str(user.id))
    session.pop('captcha_code', None)

    return success_response({
        'token': access_token,
        'user': user.to_dict(),
    }, message='登录成功')


@auth_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return error_response('用户不存在', 404)
    return success_response(user.to_dict())


@auth_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    # JWT 无状态，前端删除 token 即可
    return success_response(message='已登出')
