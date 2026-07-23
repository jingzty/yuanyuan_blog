"""
文章模块 API
- GET    /api/v1/articles           文章列表（前台/后台共用）
- GET    /api/v1/articles/<id>      文章详情
- POST   /api/v1/articles           新建文章（需登录）
- PUT    /api/v1/articles/<id>      更新文章（需登录）
- DELETE /api/v1/articles/<id>      删除文章（需登录）
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.models import db, Article, Category
from app.utils.responses import (
    success_response,
    error_response,
    paginate_response,
)

article_bp = Blueprint('article', __name__)


@article_bp.route('/articles', methods=['GET'])
def list_articles():
    """文章列表，支持分页、按状态/分类/关键词筛选"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    category_id = request.args.get('category_id', type=int)
    search = (request.args.get('search') or '').strip()
    keyword = (request.args.get('keyword') or '').strip()

    q = Article.query
    if status:
        q = q.filter(Article.status == status)
    if category_id:
        q = q.filter(Article.categories.any(Category.id == category_id))
    if search:
        q = q.filter(Article.title.ilike(f'%{search}%'))
    if keyword:
        q = q.filter(
            db.or_(
                Article.title.ilike(f'%{keyword}%'),
                Article.summary.ilike(f'%{keyword}%'),
                Article.content.ilike(f'%{keyword}%'),
            )
        )

    q = q.order_by(Article.published_at.desc().nullslast(), Article.created_at.desc())

    def serializer(a: Article):
        d = a.to_dict()
        # 兼容前台卡片需要的字段
        d['category_names'] = [c.name for c in a.categories]
        return d

    return paginate_response(q, page, per_page, serializer)


@article_bp.route('/articles/<int:article_id>', methods=['GET'])
def get_article(article_id: int):
    article = Article.query.get(article_id)
    if not article:
        return error_response('文章不存在', 404)

    # 阅读量 +1（防止快速刷新可以用 IP 限流，这里简化）
    article.view_count = (article.view_count or 0) + 1
    db.session.commit()

    data = article.to_dict(include_content=True)
    data['category_names'] = [c.name for c in article.categories]

    # 上下篇（仅当当前文章有发布时间时才查询）
    data['prev'] = None
    data['next'] = None
    if article.published_at is not None:
        prev = Article.query.filter(
            Article.published_at < article.published_at,
            Article.published_at.isnot(None),
            Article.status == 'published',
        ).order_by(Article.published_at.desc()).first()
        next_ = Article.query.filter(
            Article.published_at > article.published_at,
            Article.published_at.isnot(None),
            Article.status == 'published',
        ).order_by(Article.published_at.asc()).first()
        data['prev'] = prev.to_dict() if prev else None
        data['next'] = next_.to_dict() if next_ else None

    return success_response(data)


@article_bp.route('/articles', methods=['POST'])
@jwt_required()
def create_article():
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    content = data.get('content') or ''
    summary = (data.get('summary') or '').strip()
    cover_url = data.get('cover_url')
    status = data.get('status') or 'draft'
    category_ids = data.get('category_ids') or []
    published_at = data.get('published_at')

    if not title:
        return error_response('标题不能为空', 400)
    if not content:
        return error_response('正文不能为空', 400)
    if status not in ('draft', 'published'):
        return error_response('状态非法', 400)

    from datetime import datetime
    article = Article(
        title=title,
        summary=summary,
        content=content,
        cover_url=cover_url,
        status=status,
    )
    if published_at:
        try:
            article.published_at = datetime.fromisoformat(published_at)
        except Exception:
            pass
    if status == 'published' and not article.published_at:
        article.published_at = datetime.utcnow()

    # 关联分类
    if category_ids:
        cats = Category.query.filter(Category.id.in_(category_ids)).all()
        article.categories = cats

    db.session.add(article)
    db.session.commit()

    return success_response(article.to_dict(include_content=True), message='创建成功', code=201)


@article_bp.route('/articles/<int:article_id>', methods=['PUT'])
@jwt_required()
def update_article(article_id: int):
    article = Article.query.get(article_id)
    if not article:
        return error_response('文章不存在', 404)

    data = request.get_json() or {}
    if 'title' in data:
        article.title = (data['title'] or '').strip()
    if 'content' in data:
        article.content = data['content'] or ''
    if 'summary' in data:
        article.summary = (data['summary'] or '').strip()
    if 'cover_url' in data:
        article.cover_url = data['cover_url']
    if 'status' in data:
        if data['status'] not in ('draft', 'published'):
            return error_response('状态非法', 400)
        article.status = data['status']
        if article.status == 'published' and not article.published_at:
            from datetime import datetime
            article.published_at = datetime.utcnow()
    if 'published_at' in data and data['published_at']:
        from datetime import datetime
        try:
            article.published_at = datetime.fromisoformat(data['published_at'])
        except Exception:
            pass

    # 更新分类关联
    if 'category_ids' in data:
        cats = Category.query.filter(Category.id.in_(data['category_ids'] or [])).all()
        article.categories = cats

    db.session.commit()
    return success_response(article.to_dict(include_content=True), message='更新成功')


@article_bp.route('/articles/<int:article_id>', methods=['DELETE'])
@jwt_required()
def delete_article(article_id: int):
    article = Article.query.get(article_id)
    if not article:
        return error_response('文章不存在', 404)
    db.session.delete(article)
    db.session.commit()
    return success_response(message='删除成功')


@article_bp.route('/articles/batch', methods=['POST'])
@jwt_required()
def batch_delete_articles():
    """批量删除"""
    data = request.get_json() or {}
    ids = data.get('ids') or []
    if not ids:
        return error_response('请选择要删除的文章', 400)
    Article.query.filter(Article.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    return success_response(message=f'已删除 {len(ids)} 篇文章')


@article_bp.route('/articles/stats', methods=['GET'])
@jwt_required()
def article_stats():
    """统计卡片数据"""
    from sqlalchemy import func
    total = db.session.query(func.count(Article.id)).scalar() or 0
    published = db.session.query(func.count(Article.id)).filter(
        Article.status == 'published'
    ).scalar() or 0
    draft = db.session.query(func.count(Article.id)).filter(
        Article.status == 'draft'
    ).scalar() or 0
    from datetime import datetime, timedelta
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_new = db.session.query(func.count(Article.id)).filter(
        Article.created_at >= today_start
    ).scalar() or 0

    return success_response({
        'total': total,
        'published': published,
        'draft': draft,
        'today_new': today_new,
    })
