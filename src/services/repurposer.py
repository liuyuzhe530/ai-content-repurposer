import anthropic
import json
from typing import List, Dict, Any

class ContentRepurposer:
    """AI-powered content repurposing using Claude"""
    
    PLATFORM_CONFIGS = {
        'twitter': {
            'max_length': 280,
            'hashtag_limit': 5,
            'style': 'conversational, punchy, with emojis where appropriate',
            'structure': 'Hook first, then value, end with CTA or question'
        },
        'linkedin': {
            'max_length': 3000,
            'hashtag_limit': 5,
            'style': 'professional, thought-provoking, storytelling approach',
            'structure': 'Hook/question, personal insight, data point, call to action'
        },
        'instagram': {
            'max_length': 2200,
            'hashtag_limit': 30,
            'style': 'visually descriptive, uses line breaks, emojis',
            'structure': 'Attention-grabbing first line, body with line breaks, hashtags'
        },
        'devto': {
            'max_length': 50000,
            'hashtag_limit': 5,
            'style': 'technical, informative, code examples welcome',
            'structure': 'Clear title, intro, main content with headers, conclusion'
        }
    }
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def repurpose(self, content: str, title: str, source_type: str, target_platform: str) -> Dict[str, Any]:
        """Repurpose content for a specific platform"""
        config = self.PLATFORM_CONFIGS.get(target_platform, self.PLATFORM_CONFIGS['twitter'])
        
        prompt = self._build_prompt(content, title, source_type, target_platform, config)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_response(response.content[0].text, target_platform, config)
    
    def _build_prompt(self, content: str, title: str, source_type: str, platform: str, config: Dict) -> str:
        return f"""You are an expert content repurposing specialist. Transform content for different platforms while maintaining the core message.

## Original Content
Title: {title}
Type: {source_type}
Content:
{content[:5000]}

## Target Platform: {platform.upper()}
Requirements:
- Maximum {config['max_length']} characters
- Use {config['hashtag_limit']} or fewer hashtags
- Style: {config['style']}
- Structure: {config['structure']}

## Your Task
Create repurposed content for {platform} that:
1. Captures the key points and value proposition
2. Adapts tone and style for the platform
3. Includes relevant hashtags (max {config['hashtag_limit']})
4. Has a compelling hook/opening
5. Drives engagement

## Output Format
Return JSON with this structure:
{{
  "content": "Your repurposed content here",
  "hashtags": ["tag1", "tag2", "tag3"],
  "hook": "The attention-grabbing first line",
  "cta": "Call to action (if appropriate)"
}}

Only return the JSON, no other text. Make the content genuinely engaging and platform-native.
"""
    
    def _parse_response(self, response_text: str, platform: str, config: Dict) -> Dict[str, Any]:
        try:
            if response_text.strip().startswith('{'):
                result = json.loads(response_text)
            else:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    result = json.loads(response_text[json_start:json_end])
                else:
                    result = self._fallback_parse(response_text, platform, config)
        except json.JSONDecodeError:
            result = self._fallback_parse(response_text, platform, config)
        
        # Ensure hashtags exist
        if 'hashtags' not in result:
            result['hashtags'] = []
        
        # Ensure content exists
        if 'content' not in result:
            result['content'] = response_text
        
        result['character_count'] = len(result['content'])
        
        return result
    
    def _fallback_parse(self, text: str, platform: str, config: Dict) -> Dict[str, Any]:
        """Fallback parsing when JSON is not properly formatted"""
        lines = text.strip().split('\n')
        
        # Try to extract hashtags
        hashtags = []
        for line in lines:
            if line.startswith('#'):
                tags = [t.strip() for t in line.split() if t.startswith('#')]
                hashtags.extend(tags)
        
        # Extract first non-empty line as hook
        hook = next((l.strip() for l in lines if l.strip() and not l.strip().startswith('{')), '')
        
        return {
            'content': text.strip(),
            'hashtags': hashtags[:config['hashtag_limit']],
            'hook': hook,
            'cta': ''
        }
    
    def repurpose_all(self, content: str, title: str, source_type: str) -> Dict[str, Dict[str, Any]]:
        """Repurpose content for all supported platforms"""
        platforms = ['twitter', 'linkedin', 'instagram', 'devto']
        results = {}
        
        for platform in platforms:
            try:
                results[platform] = self.repurpose(content, title, source_type, platform)
            except Exception as e:
                results[platform] = {
                    'content': f'Error repurposing for {platform}: {str(e)}',
                    'hashtags': [],
                    'hook': '',
                    'cta': ''
                }
        
        return results
    
    def generate_thread(self, content: str, title: str, num_tweets: int = 5) -> Dict[str, Any]:
        """Generate a Twitter thread from content"""
        prompt = f"""You are an expert Twitter thread creator. Transform this content into an engaging thread.

## Original Content
Title: {title}
Content:
{content[:5000]}

## Thread Requirements
- Create exactly {num_tweets} tweets
- Each tweet max 280 characters
- First tweet: Hook/attention grabber with "1/"
- Middle tweets: Value delivery, one point each
- Last tweet: CTA or conclusion with "THREAD" note

## Output Format
Return JSON:
{{
  "tweets": [
    {{"text": "Tweet 1 content", "number": "1/"}},
    {{"text": "Tweet 2 content", "number": "2/"}},
    ...
  ]
}}

Only return the JSON.
"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            result = json.loads(response.content[0].text)
        except:
            result = {'tweets': [{'text': response.content[0].text, 'number': '1/'}]}
        
        return result
