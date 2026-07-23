"""
Flask 应用工厂
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from app.config import config
from app.models import db
from app.utils.responses import error_response


def create_app(config_name: str = 'default') -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # ============ 扩展初始化 ============
    db.init_app(app)
    JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}},
         supports_credentials=True)

    # ============ 注册蓝图 ============
    from app.api.auth import auth_bp
    from app.api.article import article_bp
    from app.api.category import category_bp
    from app.api.banner import banner_bp
    from app.api.featured import featured_bp
    from app.api.profile import profile_bp

    app.register_blueprint(auth_bp, url_prefix='/api/v1')
    app.register_blueprint(article_bp, url_prefix='/api/v1')
    app.register_blueprint(category_bp, url_prefix='/api/v1')
    app.register_blueprint(banner_bp, url_prefix='/api/v1')
    app.register_blueprint(featured_bp, url_prefix='/api/v1')
    app.register_blueprint(profile_bp, url_prefix='/api/v1')

    # ============ 全局错误处理 ============
    @app.errorhandler(400)
    def bad_request(e):
        return error_response('请求参数错误', 400)

    @app.errorhandler(401)
    def unauthorized(e):
        return error_response('未授权，请登录', 401)

    @app.errorhandler(404)
    def not_found(e):
        return error_response('资源不存在', 404)

    @app.errorhandler(500)
    def server_error(e):
        return error_response('服务器内部错误', 500)

    # ============ 健康检查 ============
    @app.route('/api/v1/health')
    def health():
        return jsonify({'status': 'ok', 'service': 'yuanyuan-blog-backend'})

    # ============ 数据库初始化 + 默认数据 seed ============
    with app.app_context():
        db.create_all()
        _seed_default_data()

    return app


def _seed_default_data():
    """启动时自动创建默认 admin 账号 + 示例分类"""
    from app.models import User, Category

    # 默认管理员
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        print('[Seed] 默认管理员已创建: admin / admin123')

    # 示例分类
    default_categories = ['前端开发', '后端架构', '工具效率', 'AI 探索', '生活随笔']
    for name in default_categories:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
    print('[Seed] 默认分类已确保存在')

    db.session.commit()
