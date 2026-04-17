from flask import Blueprint, request, jsonify
import uuid
from src.models import ContentStore, ContentSource, RepurposedContent

api_bp = Blueprint('api', __name__, url_prefix='/api')
store = ContentStore()

@api_bp.route('/fetch', methods=['POST'])
def fetch_content():
    """Fetch content from a URL"""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    from src.services.content_fetcher import ContentFetcher
    fetcher = ContentFetcher()
    result = fetcher.fetch_url(url)
    
    if 'error' in result and result.get('error'):
        return jsonify({'error': result['error']}), 400
    
    # Save as source
    source = ContentSource(
        id=str(uuid.uuid4()),
        source_type=result.get('type', 'blog'),
        url=url,
        title=result.get('title', 'Untitled'),
        original_content=result.get('content', '')
    )
    store.add_source(source)
    
    result['source_id'] = source.id
    return jsonify(result)

@api_bp.route('/repurpose', methods=['POST'])
def repurpose():
    """Repurpose content for a platform"""
    data = request.get_json()
    source_id = data.get('source_id')
    platform = data.get('platform', 'all')
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'API key required'}), 400
    
    source = store.get_source(source_id)
    if not source:
        return jsonify({'error': 'Source not found'}), 404
    
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
    
    return jsonify({'success': True, 'results': results})

@api_bp.route('/thread', methods=['POST'])
def generate_thread():
    """Generate a Twitter thread"""
    data = request.get_json()
    source_id = data.get('source_id')
    num_tweets = data.get('num_tweets', 5)
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'API key required'}), 400
    
    source = store.get_source(source_id)
    if not source:
        return jsonify({'error': 'Source not found'}), 404
    
    from src.services.repurposer import ContentRepurposer
    repurposer = ContentRepurposer(api_key)
    result = repurposer.generate_thread(source.original_content, source.title, num_tweets)
    
    return jsonify({'success': True, 'thread': result})

@api_bp.route('/schedule', methods=['POST'])
def create_schedule():
    """Schedule a post for publishing"""
    data = request.get_json()
    content_id = data.get('content_id')
    platform = data.get('platform')
    scheduled_time = data.get('scheduled_time')  # ISO format
    
    if not all([content_id, platform, scheduled_time]):
        return jsonify({'error': 'content_id, platform, and scheduled_time required'}), 400
    
    from datetime import datetime
    from src.services.scheduler import schedule_post
    
    dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
    schedule = schedule_post(content_id, platform, dt)
    
    return jsonify({'success': True, 'schedule_id': schedule.id})

@api_bp.route('/sources', methods=['GET'])
def list_sources():
    """List all content sources"""
    return jsonify({'sources': [
        {
            'id': s.id,
            'type': s.source_type,
            'url': s.url,
            'title': s.title,
            'created_at': s.created_at.isoformat()
        } for s in store.sources
    ]})

@api_bp.route('/sources/<source_id>/repurposed', methods=['GET'])
def list_repurposed(source_id):
    """List repurposed content for a source"""
    items = store.get_repurposed_for_source(source_id)
    return jsonify({'items': [
        {
            'id': r.id,
            'platform': r.platform,
            'content': r.content,
            'hashtags': r.hashtags,
            'character_count': r.character_count,
            'created_at': r.created_at.isoformat()
        } for r in items
    ]})
