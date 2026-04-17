import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re
from typing import Optional
import html2text

class ContentFetcher:
    """Fetch content from various sources"""
    
    def __init__(self):
        self.h = html2text.HTML2Text()
        self.h.ignore_links = False
        self.h.body_width = 0
    
    def fetch_url(self, url: str) -> dict:
        """Fetch content from any URL"""
        if 'youtube.com' in url or 'youtu.be' in url:
            return self.fetch_youtube(url)
        elif 'twitter.com' in url or 'x.com' in url:
            return self.fetch_twitter(url)
        else:
            return self.fetch_blog(url)
    
    def fetch_blog(self, url: str) -> dict:
        """Fetch and parse blog article"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Remove script and style elements
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                tag.decompose()
            
            # Try to find the main content
            article = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile(r'content|article|post|entry'))
            
            if article:
                content = article.get_text(separator='\n', strip=True)
            else:
                # Fallback to body
                body = soup.find('body')
                content = body.get_text(separator='\n', strip=True) if body else resp.text
            
            # Clean up excessive newlines
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            # Get title
            title = soup.find('h1')
            if not title:
                title = soup.find('title')
            title_text = title.get_text(strip=True) if title else url
            
            return {
                'type': 'blog',
                'url': url,
                'title': title_text,
                'content': content,
                'word_count': len(content.split())
            }
        except Exception as e:
            return {'type': 'blog', 'url': url, 'error': str(e)}
    
    def fetch_youtube(self, url: str) -> dict:
        """Fetch YouTube video transcript"""
        try:
            # Extract video ID
            video_id = self._extract_youtube_id(url)
            if not video_id:
                return {'type': 'youtube', 'url': url, 'error': 'Invalid YouTube URL'}
            
            # Try to get transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            content = ' '.join([entry['text'] for entry in transcript])
            
            # Get video title via API
            try:
                api_url = f'https://noembed.com/embed?url={url}'
                meta = requests.get(api_url, timeout=5).json()
                title = meta.get('title', 'YouTube Video')
            except:
                title = 'YouTube Video'
            
            return {
                'type': 'youtube',
                'url': url,
                'video_id': video_id,
                'title': title,
                'content': content,
                'word_count': len(content.split()),
                'duration': sum(entry['duration'] for entry in transcript)
            }
        except TranscriptsDisabled:
            return {'type': 'youtube', 'url': url, 'error': 'Transcripts are disabled for this video'}
        except NoTranscriptFound:
            return {'type': 'youtube', 'url': url, 'error': 'No English transcript found'}
        except Exception as e:
            return {'type': 'youtube', 'url': url, 'error': str(e)}
    
    def fetch_twitter(self, url: str) -> dict:
        """Fetch tweet content (simplified - requires Twitter API for full access)"""
        # Note: Full Twitter/X scraping requires API access
        return {
            'type': 'twitter',
            'url': url,
            'title': 'Tweet',
            'content': 'Twitter content requires API access. Please use another source.',
            'error': None
        }
    
    def _extract_youtube_id(self, url: str) -> Optional[str]:
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
