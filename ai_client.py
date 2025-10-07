import os, base64, re
from PIL import Image, ImageDraw, ImageFont

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

def _stub_text(topic, language='English'):
    title = f"{topic} - Demo Title ({language})"
    content = f"## Introduction\nThis is a demo {language} article about {topic}."
    meta = f"Demo meta for {topic}"
    hashtags = ['#demo','#ai','#seo','#blog','#content']
    return {'title': title, 'content': content, 'meta_desc': meta, 'hashtags': hashtags}

def generate_seo_blog_text(topic: str, language: str = 'English', keywords: str = None, location: str = None):
    if not OPENAI_API_KEY:
        return _stub_text(topic, language)
    # TODO: call OpenAI ChatCompletion to generate SEO-optimized content.
    return _stub_text(topic, language)

def generate_images_stub(topic, count=3):
    out = []
    os.makedirs('backend/static/uploads', exist_ok=True)
    for i in range(count):
        filename = f"img_{abs(hash(topic))%100000}_{i}.png"
        path = os.path.join('backend','static','uploads', filename)
        img = Image.new('RGB', (1200,630), color=(200,220,255))
        d = ImageDraw.Draw(img)
        text = f"{topic}\nImage {i+1}"
        try:
            font = ImageFont.load_default()
            d.text((20,20), text, fill=(0,0,0), font=font)
        except Exception:
            d.text((20,20), text, fill=(0,0,0))
        img.save(path)
        out.append({"url": f"/static/uploads/{filename}", "alt": f"{topic} image {i+1}", "source": "ai"})
    return out

def save_image_to_s3(img_bytes: bytes, prompt: str, index=0):
    bucket = AWS_S3_BUCKET
    region = AWS_REGION or 'us-east-1'
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', prompt)[:50]
    key = f"blog_images/{safe_name}_{index}.png"
    if not bucket:
        os.makedirs('backend/static/uploads', exist_ok=True)
        path = os.path.join('backend','static','uploads', key.replace('/','_'))
        with open(path, 'wb') as f:
            f.write(img_bytes)
        return f"/static/uploads/{os.path.basename(path)}"
    try:
        import boto3
        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket, Key=key, Body=img_bytes, ContentType='image/png', ACL='public-read')
        url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
        return url
    except Exception:
        os.makedirs('backend/static/uploads', exist_ok=True)
        path = os.path.join('backend','static','uploads', key.replace('/','_'))
        with open(path, 'wb') as f:
            f.write(img_bytes)
        return f"/static/uploads/{os.path.basename(path)}"

def generate_images_openai(prompt: str, count: int = 3, size: str = '1024x1024'):
    if not OPENAI_API_KEY:
        return generate_images_stub(prompt, count=count)
    try:
        import openai, base64
        openai.api_key = OPENAI_API_KEY
        results = []
        for i in range(count):
            resp = openai.images.generate(model='gpt-image-1', prompt=prompt, size=size)
            b64 = resp.data[0].b64_json
            img_bytes = base64.b64decode(b64)
            url = save_image_to_s3(img_bytes, prompt, index=i)
            results.append({'url': url, 'alt': prompt, 'source': 'ai'})
        return results
    except Exception as e:
        return [{'error':'image_generation_failed', 'details': str(e)}]
