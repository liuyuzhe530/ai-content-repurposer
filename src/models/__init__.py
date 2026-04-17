from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import json

@dataclass
class ContentSource:
    id: str
    source_type: str  # 'blog', 'youtube', 'twitter', 'rss'
    url: str
    title: str
    original_content: str
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class RepurposedContent:
    id: str
    source_id: str
    platform: str  # 'twitter', 'linkedin', 'instagram', 'devto'
    content: str
    hashtags: List[str] = field(default_factory=list)
    character_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    published: bool = False
    published_at: Optional[datetime] = None

@dataclass
class Schedule:
    id: str
    platform: str
    content_id: str
    scheduled_time: datetime
    status: str = 'pending'  # pending, sent, failed
    sent_at: Optional[datetime] = None

class ContentStore:
    """Simple JSON-based content store for demonstration"""
    
    def __init__(self, path: str = 'data/content.json'):
        self.path = path
        self.sources: List[ContentSource] = []
        self.repurposed: List[RepurposedContent] = []
        self.schedules: List[Schedule] = []
        self._load()
    
    def _load(self):
        import os
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                data = json.load(f)
                self.sources = [ContentSource(**s) for s in data.get('sources', [])]
                self.repurposed = [RepurposedContent(**r) for r in data.get('repurposed', [])]
                self.schedules = [Schedule(**s) for s in data.get('schedules', [])]
    
    def _save(self):
        import os
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'w') as f:
            json.dump({
                'sources': [s.__dict__ for s in self.sources],
                'repurposed': [r.__dict__ for r in self.repurposed],
                'schedules': [s.__dict__ for s in self.schedules],
            }, f, default=str)
    
    def add_source(self, source: ContentSource):
        self.sources.append(source)
        self._save()
    
    def add_repurposed(self, content: RepurposedContent):
        self.repurposed.append(content)
        self._save()
    
    def add_schedule(self, schedule: Schedule):
        self.schedules.append(schedule)
        self._save()
    
    def get_source(self, source_id: str) -> Optional[ContentSource]:
        return next((s for s in self.sources if s.id == source_id), None)
    
    def get_repurposed_for_source(self, source_id: str) -> List[RepurposedContent]:
        return [r for r in self.repurposed if r.source_id == source_id]
    
    def get_schedules(self, status: str = None) -> List[Schedule]:
        if status:
            return [s for s in self.schedules if s.status == status]
        return self.schedules
    
    def mark_sent(self, schedule_id: str):
        for s in self.schedules:
            if s.id == schedule_id:
                s.status = 'sent'
                s.sent_at = datetime.utcnow()
        self._save()
    
    def mark_published(self, content_id: str):
        for r in self.repurposed:
            if r.id == content_id:
                r.published = True
                r.published_at = datetime.utcnow()
        self._save()
