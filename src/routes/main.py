from flask import Blueprint, render_template, request, session, redirect, url_for
import uuid
from src.models import ContentStore, ContentSource, RepurposedContent

main_bp = Blueprint('main', __name__)
store = ContentStore()

@main_bp.route('/')
def index():
    sources = store.sources[-10:][::-1]  # Last 10, reversed
    return render_template('index.html', sources=sources)

@main_bp.route('/source/new', methods=['GET', 'POST'])
def new_source():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return render_template('new_source.html', error='URL is required')
        
        from src.services.content_fetcher import ContentFetcher
        fetcher = ContentFetcher()
        data = fetcher.fetch_url(url)
        
        if 'error' in data and data.get('error'):
            return render_template('new_source.html', error=data['error'])
        
        source = ContentSource(
            id=str(uuid.uuid4()),
            source_type=data.get('type', 'blog'),
            url=url,
            title=data.get('title', 'Untitled'),
            original_content=data.get('content', '')
        )
        
        store.add_source(source)
        return redirect(url_for('main.view_source', source_id=source.id))
    
    return render_template('new_source.html')

@main_bp.route('/source/<source_id>')
def view_source(source_id):
    source = store.get_source(source_id)
    if not source:
        return "Source not found", 404
    
    repurposed = store.get_repurposed_for_source(source_id)
    return render_template('source_detail.html', source=source, repurposed=repurposed)

@main_bp.route('/source/<source_id>/repurpose', methods=['POST'])
def repurpose_source(source_id):
    source = store.get_source(source_id)
    if not source:
        return "Source not found", 404
    
    platform = request.form.get('platform', 'all')
    api_key = request.environ.get('ANTHROPIC_API_KEY') or request.form.get('api_key')
    
    if not api_key:
        return render_template('source_detail.html', source=source, repurposed=[], error='API key required')
    
    from src.services.repurposer import ContentRepurposer
    repurposer = ContentRepurposer(api_key)
    
    if platform == 'all':
        results = repurposer.repurpose_all(source.original_content, source.title, source.source_type)
    else:
        results = {platform: repurposer.repurpose(source.original_content, source.title, source.source_type, platform)}
    
    # Save repurposed content
    for plat, result in results.items():
        content = RepurposedContent(
            id=str(uuid.uuid4()),
            source_id=source_id,
            platform=plat,
            content=result.get('content', ''),
            hashtags=result.get('hashtags', []),
            character_count=result.get('character_count', 0)
        )
        store.add_repurposed(content)
    
    repurposed = store.get_repurposed_for_source(source_id)
    return render_template('source_detail.html', source=source, repurposed=repurposed, results=results)

@main_bp.route('/source/<source_id>/repurpose/api', methods=['POST'])
def repurpose_api(source_id):
    """API endpoint for repurposing"""
    source = store.get_source(source_id)
    if not source:
        return {'error': 'Source not found'}, 404
    
    data = request.get_json()
    platform = data.get('platform', 'all')
    api_key = data.get('api_key')
    
    if not api_key:
        return {'error': 'API key required'}, 400
    
    from src.services.repurposer import ContentRepurposer
    repurposer = ContentRepurposer(api_key)
    
    if platform == 'all':
        results = repurposer.repurpose_all(source.original_content, source.title, source.source_type)
    else:
        results = {platform: repurposer.repurpose(source.original_content, source.title, source.source_type, platform)}
    
    # Save
    for plat, result in results.items():
        content = RepurposedContent(
            id=str(uuid.uuid4()),
            source_id=source_id,
            platform=plat,
            content=result.get('content', ''),
            hashtags=result.get('hashtags', []),
            character_count=result.get('character_count', 0)
        )
        store.add_repurposed(content)
    
    return {'success': True, 'results': results}

@main_bp.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if request.method == 'POST':
        content_id = request.form.get('content_id')
        platform = request.form.get('platform')
        date = request.form.get('date')
        time = request.form.get('time')
        
        from datetime import datetime
        scheduled_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        
        from src.services.scheduler import schedule_post
        schedule_post(content_id, platform, scheduled_time)
        
        return redirect(url_for('main.schedule'))
    
    pending = store.get_schedules('pending')
    return render_template('schedule.html', schedules=pending)
