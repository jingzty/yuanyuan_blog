"""
远远的天空 — 数据库模型
技术栈：Flask-SQLAlchemy
数据库：SQLite
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

now_utc = lambda: datetime.now(timezone.utc)

db = SQLAlchemy()


# ============ 文章-分类 多对多中间表 ============
article_category = db.Table(
    'article_category',
    db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
)


# ============ 用户（单博主）============
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=now_utc, nullable=False)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ============ 分类 ============
class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=now_utc, nullable=False)

    articles = db.relationship(
        'Article',
        secondary=article_category,
        back_populates='categories',
    )

    def to_dict(self, include_count: bool = False):
        data = {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_count:
            data['article_count'] = len(self.articles)
        return data


# ============ 文章 ============
class Article(db.Model):
    __tablename__ = 'article'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    summary = db.Column(db.String(500), nullable=True)
    content = db.Column(db.Text, nullable=False)
    cover_url = db.Column(db.String(500), nullable=True)
    view_count = db.Column(db.Integer, default=0, nullable=False)

    # 状态：draft / published
    status = db.Column(db.String(20), default='draft', nullable=False, index=True)

    published_at = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=now_utc, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=now_utc,
        onupdate=now_utc,
        nullable=False,
    )

    categories = db.relationship(
        'Category',
        secondary=article_category,
        back_populates='articles',
    )

    def to_dict(self, include_content: bool = False):
        data = {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'cover_url': self.cover_url,
            'view_count': self.view_count,
            'status': self.status,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'categories': [c.to_dict() for c in self.categories],
        }
        if include_content:
            data['content'] = self.content
        return data


# ============ 轮播图 ============
class Banner(db.Model):
    __tablename__ = 'banner'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(500), nullable=True)
    image_url = db.Column(db.String(500), nullable=False)
    link_url = db.Column(db.String(500), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False, index=True)

    # 状态：enabled / disabled
    status = db.Column(db.String(20), default='enabled', nullable=False, index=True)

    created_at = db.Column(db.DateTime, default=now_utc, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=now_utc,
        onupdate=now_utc,
        nullable=False,
    )

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'subtitle': self.subtitle,
            'image_url': self.image_url,
            'link_url': self.link_url,
            'sort_order': self.sort_order,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# ============ 文章推荐 ============
class FeaturedArticle(db.Model):
    __tablename__ = 'featured_article'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False, unique=True, index=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False, index=True)

    # 状态：enabled / disabled
    status = db.Column(db.String(20), default='enabled', nullable=False, index=True)

    created_at = db.Column(db.DateTime, default=now_utc, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=now_utc,
        onupdate=now_utc,
        nullable=False,
    )

    article = db.relationship('Article', backref='featured_entry')

    def to_dict(self, include_article: bool = True):
        data = {
            'id': self.id,
            'article_id': self.article_id,
            'sort_order': self.sort_order,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_article and self.article:
            a = self.article
            data['article'] = {
                'id': a.id,
                'title': a.title,
                'summary': a.summary,
                'cover_url': a.cover_url,
                'status': a.status,
                'published_at': a.published_at.isoformat() if a.published_at else None,
                'created_at': a.created_at.isoformat() if a.created_at else None,
                'categories': [c.to_dict() for c in a.categories],
            }
        return data


# ============ 博主资料 ============
class Profile(db.Model):
    __tablename__ = 'profile'

    id = db.Column(db.Integer, primary_key=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    nickname = db.Column(db.String(64), nullable=False, default='远远')
    bio = db.Column(db.Text, nullable=True)
    social_links = db.Column(db.Text, nullable=True)  # JSON 格式
    updated_at = db.Column(
        db.DateTime,
        default=now_utc,
        onupdate=now_utc,
        nullable=False,
    )

    def to_dict(self):
        import json
        social = []
        if self.social_links:
            try:
                social = json.loads(self.social_links)
            except Exception:
                social = []
        return {
            'id': self.id,
            'avatar_url': self.avatar_url,
            'nickname': self.nickname,
            'bio': self.bio,
            'social_links': social,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
