from flask import Blueprint, request, jsonify, send_from_directory
from models import SessionLocal, Blog, User
from ai_client import generate_seo_blog_text, generate_images_openai
from utils import keyword_density, readability_score, simple_plagiarism_check
import os, json

blog_bp = Blueprint('blog', __name__)

def _check_and_decrement_quota(user_id):
    db = SessionLocal()
    user = db.query(User).filter(User.id==user_id).first()
    if not user:
        db.close()
        return True, None
    if user.plan == 'premium':
        db.close()
        return True, None
    if user.blogs_left is None:
        db.close()
        return True, None
    if user.blogs_left <= 0:
        db.close()
        return False, 'quota_exhausted'
    user.blogs_left = user.blogs_left - 1
    db.add(user); db.commit(); db.close()
    return True, None

@blog_bp.route('/generate', methods=['POST'])
def generate():
    data = request.json or {}
    user_id = data.get('user_id', 'demo-user')
    keyword = data.get('keyword')
    language = data.get('language', 'English')
    translate = data.get('translate', False)
    location = data.get('location')

    if not keyword:
        return jsonify({'error':'keyword_required'}), 400

    ok, reason = _check_and_decrement_quota(user_id)
    if not ok:
        return jsonify({'error': reason}), 402

    # Generate English base then translate if requested
    base_text = generate_seo_blog_text(keyword, language='English', keywords=keyword, location=location)
    original_content = base_text.get('content')

    translated_content = None
    if translate and language.lower() != 'english':
        translated_text = generate_seo_blog_text(keyword, language=language, keywords=keyword, location=location)
        translated_content = translated_text.get('content')

    prompt = f"High quality hero image for: {keyword}. Professional, minimal composition, vibrant colors"
    images = generate_images_openai(prompt, count=3)

    db = SessionLocal()
    blog = Blog(user_id=user_id, keyword=keyword, title=base_text.get('title'), meta_desc=base_text.get('meta_desc'),
                hashtags=base_text.get('hashtags'), content_original=original_content, content_translated=translated_content,
                language=language, images=images, selected_image=(images[0]['url'] if images else None))
    db.add(blog); db.commit(); db.refresh(blog); db.close()

    density = keyword_density(original_content or '', keyword)
    readability = readability_score(original_content or '')
    plagiarism = simple_plagiarism_check(original_content or '', [])

    return jsonify({'blog_id': blog.id, 'original': original_content, 'translated': translated_content, 'images': images,
                    'keyword_density': density, 'readability': readability, 'plagiarism': plagiarism})

@blog_bp.route('/<blog_id>', methods=['GET'])
def get_blog(blog_id):
    db = SessionLocal()
    blog = db.query(Blog).filter(Blog.id==blog_id).first()
    db.close()
    if not blog:
        return jsonify({'error':'not_found'}), 404
    return jsonify({
        'id': blog.id,
        'keyword': blog.keyword,
        'title': blog.title,
        'meta_desc': blog.meta_desc,
        'hashtags': blog.hashtags,
        'content_original': blog.content_original,
        'content_translated': blog.content_translated,
        'language': blog.language,
        'images': blog.images or [],
        'selected_image': blog.selected_image,
        'status': blog.status
    })

@blog_bp.route('/update/<blog_id>', methods=['PUT'])
def update(blog_id):
    data = request.json or {}
    db = SessionLocal()
    blog = db.query(Blog).filter(Blog.id==blog_id).first()
    if not blog:
        db.close(); return jsonify({'error':'not_found'}), 404
    blog.title = data.get('title', blog.title)
    blog.meta_desc = data.get('meta_desc', blog.meta_desc)
    if data.get('content_original') is not None:
        blog.content_original = data.get('content_original')
    if data.get('content_translated') is not None:
        blog.content_translated = data.get('content_translated')
    blog.hashtags = data.get('hashtags', blog.hashtags)
    sel_img = data.get('selected_image')
    if sel_img:
        blog.selected_image = sel_img
    blog.status = data.get('status', blog.status)
    db.add(blog); db.commit(); db.refresh(blog); db.close()
    return jsonify({'status':'ok', 'blog_id': blog.id})

@blog_bp.route('/images/generate', methods=['POST'])
def images_generate():
    data = request.json or {}
    topic = data.get('topic')
    count = int(data.get('count', 3))
    prompt = data.get('prompt') or f"High quality photo about {topic}, professional, hero header"
    imgs = generate_images_openai(prompt, count=count)
    return jsonify({'images': imgs})

@blog_bp.route('/images/upload', methods=['POST'])
def images_upload():
    file = request.files.get('file')
    blog_id = request.form.get('blog_id')
    if not file:
        return jsonify({'error':'file_required'}), 400
    upload_dir = os.path.join('backend','static','uploads')
    os.makedirs(upload_dir, exist_ok=True)
    filename = file.filename
    path = os.path.join(upload_dir, filename)
    file.save(path)
    url = f"/static/uploads/{filename}"
    try:
        import boto3
        bucket = os.getenv('AWS_S3_BUCKET')
        region = os.getenv('AWS_REGION', 'us-east-1')
        if bucket:
            s3 = boto3.client('s3')
            key = f"user_uploads/{filename}"
            with open(path, 'rb') as f:
                s3.put_object(Bucket=bucket, Key=key, Body=f, ContentType='image/png', ACL='public-read')
            url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
    except Exception:
        pass
    if blog_id:
        db = SessionLocal()
        blog = db.query(Blog).filter(Blog.id==blog_id).first()
        if blog:
            imgs = blog.images or []
            imgs.append({'url': url, 'alt': filename, 'source': 'user'})
            blog.images = imgs
            db.add(blog); db.commit(); db.refresh(blog)
        db.close()
    return jsonify({'url': url})

@blog_bp.route('/static/uploads/<path:filename>', methods=['GET'])
def serve_uploads(filename):
    return send_from_directory(os.path.join('backend','static','uploads'), filename)
