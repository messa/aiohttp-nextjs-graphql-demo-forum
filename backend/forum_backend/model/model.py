import asyncio
from datetime import datetime
import yaml
from uuid import uuid4


dummy_data = yaml.load('''
    categories:
        cat1:
            title: Category 1
            topic_ids: [ top1, top2 ]
        cat2:
            title: Category 2
            topic_ids: [ top3, top4, top5 ]
    topics:
        top1:
            title: Topic 1
            conversation_id: conv1
        top2:
            title: Topic 2
            conversation_id: conv2
        top3:
            title: Topic 3
            conversation_id: conv3
        top4:
            title: Topic 4
            conversation_id: conv4
        top5:
            title: Topic 5
            conversation_id: conv5
    conversations:
        conv1: {}
        conv2: {}
        conv3: {}
        conv4: {}
        conv5: {}
    conversation_posts:
        cp1:
            conversation_id: conv1
            body_markdown: "Cool!"
            create_date: 2019-01-12T12:00:00Z
        cp2:
            conversation_id: conv1
            reply_to_post_id: cp1
            body_markdown: "Indeed!"
            create_date: 2019-01-12T13:00:00Z
        cp3:
            conversation_id: conv1
            body_markdown: "Hello!"
            create_date: 2019-01-12T11:00:00Z
''')


class Model:

    async def get_by_id(self, id):
        await asyncio.sleep(.01)
        for cat_id, cat in dummy_data['categories'].items():
            if cat_id == id:
                return Category(cat_id, **cat)
        for p_id, p_data in dummy_data['conversation_posts'].items():
            if p_id == id:
                return Post(p_id, **p_data)
        for t_id, t_data in dummy_data['topics'].items():
            if t_id == id:
                return Topic(t_id, **t_data)
        for c_id, c_data in dummy_data['conversations'].items():
            if c_id == id:
                return Conversation(c_id, **c_data)
        return None

    async def list_categories(self):
        await asyncio.sleep(.01)
        categories = []
        for cat_id, cat in dummy_data['categories'].items():
            categories.append(Category(cat_id, **cat))
        return categories

    async def get_topic(self, topic_id):
        await asyncio.sleep(.01)
        return Topic(topic_id, **dummy_data['topics'][topic_id])

    async def get_conversation(self, conversation_id):
        await asyncio.sleep(.01)
        return Conversation(
            conversation_id,
            **dummy_data['conversations'][conversation_id])

    async def list_conversation_posts(self, conversation_id):
        await asyncio.sleep(.01)
        posts = []
        for post_id, post_data in dummy_data['conversation_posts'].items():
            if post_data['conversation_id'] != conversation_id:
                continue
            if post_data.get('reply_to_post_id'):
                continue
            posts.append(Post(post_id, **post_data))
        return posts

    async def list_post_replies(self, post_id):
        await asyncio.sleep(.01)
        replies = []
        for p_id, p_data in dummy_data['conversation_posts'].items():
            if p_data.get('reply_to_post_id') != post_id:
                continue
            replies.append(Post(p_id, **p_data))
        return replies

    async def create_reply_post(self, parent_post_id, body_markdown):
        await asyncio.sleep(.01)
        parent_post = dummy_data['conversation_posts'][parent_post_id]
        new_post_id = 'cp' + uuid4().hex[:9]
        assert new_post_id not in dummy_data['conversation_posts']
        dummy_data['conversation_posts'][new_post_id] = {
            'conversation_id': parent_post['conversation_id'],
            'body_markdown': body_markdown,
            'create_date': datetime.utcnow(),
            'reply_to_post_id': parent_post.get('reply_to_post_id') or parent_post_id,
        }
        return Post(new_post_id, **dummy_data['conversation_posts'][new_post_id])


class Category:

    node_type = 'Category'

    def __init__(self, category_id, title, topic_ids):
        assert isinstance(topic_ids, list)
        self.id = category_id
        self.title = title
        self.topic_ids = topic_ids


class Topic:

    node_type = 'Topic'

    def __init__(self, category_id, title, conversation_id):
        self.id = category_id
        self.title = title
        self.conversation_id = conversation_id


class Conversation:

    node_type = 'Conversation'

    def __init__(self, conversation_id):
        self.id = conversation_id


class Post:

    node_type = 'Post'

    def __init__(self, post_id, create_date, body_markdown, conversation_id, reply_to_post_id=None):
        self.id = post_id
        self.create_date = parse_date(create_date)
        self.body_markdown = body_markdown
        self.conversation_id = conversation_id
        self.reply_to_post_id = reply_to_post_id


def parse_date(dt):
    if isinstance(dt, datetime):
        return dt
    raise Exception(f'Unable to parse_date: {dt!r}')
