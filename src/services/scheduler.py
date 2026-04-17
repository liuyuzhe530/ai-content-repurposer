from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def init_scheduler(app):
    """Initialize the job scheduler"""
    
    def cleanup_old_schedule():
        """Clean up old scheduled posts"""
        from src.models import ContentStore
        store = ContentStore()
        
        # Mark overdue pending items as failed
        now = datetime.utcnow()
        for schedule in store.schedules:
            if schedule.status == 'pending' and schedule.scheduled_time < now:
                schedule.status = 'failed'
        
        logger.info("Scheduler cleanup completed")
    
    def sync_feeds():
        """Sync content from RSS feeds"""
        logger.info("RSS feed sync triggered")
        # This would sync from configured RSS feeds
    
    # Run cleanup every hour
    scheduler.add_job(
        cleanup_old_schedule,
        CronTrigger(minute=0),
        id='cleanup_job',
        name='Cleanup old scheduled posts',
        replace_existing=True
    )
    
    # Run RSS sync every 30 minutes
    scheduler.add_job(
        sync_feeds,
        CronTrigger(minute='*/30'),
        id='rss_sync_job',
        name='Sync RSS feeds',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started")

def schedule_post(content_id: str, platform: str, scheduled_time: datetime):
    """Schedule a post for publishing"""
    from src.models import ContentStore, Schedule
    import uuid
    
    store = ContentStore()
    
    schedule = Schedule(
        id=str(uuid.uuid4()),
        platform=platform,
        content_id=content_id,
        scheduled_time=scheduled_time
    )
    
    store.add_schedule(schedule)
    
    # Add to scheduler
    def publish_job():
        _publish_scheduled_post(schedule.id)
    
    scheduler.add_job(
        publish_job,
        'date',
        run_date=scheduled_time,
        id=f'post_{schedule.id}',
        name=f'Publish {platform} post',
        replace_existing=True
    )
    
    return schedule

def _publish_scheduled_post(schedule_id: str):
    """Internal function to publish a scheduled post"""
    from src.models import ContentStore
    
    store = ContentStore()
    
    schedule = next((s for s in store.schedules if s.id == schedule_id), None)
    if not schedule:
        logger.error(f"Schedule {schedule_id} not found")
        return
    
    if schedule.status != 'pending':
        return
    
    try:
        # Here you would integrate with actual publishing APIs
        # For now, just mark as sent
        
        # Example integrations would be:
        # - Twitter API for Twitter posts
        # - LinkedIn API for LinkedIn posts
        # - Dev.to API for Dev.to articles
        
        store.mark_sent(schedule_id)
        logger.info(f"Published scheduled post {schedule_id} for {schedule.platform}")
        
    except Exception as e:
        schedule.status = 'failed'
        logger.error(f"Failed to publish {schedule_id}: {e}")
