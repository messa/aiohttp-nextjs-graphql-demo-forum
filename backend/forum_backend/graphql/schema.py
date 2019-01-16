from asyncio import create_task
from functools import wraps
from inspect import iscoroutinefunction
from graphql import (
    graphql,
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLField,
    GraphQLNonNull,
    GraphQLString,
    GraphQLList,
    GraphQLID
)


def with_model(f):
    assert iscoroutinefunction(f)
    async def wrapper(parent, info, *args, **kwargs):
        assert 'model' not in kwargs
        model = info.context['request'].app['model']
        return await f(parent, info, *args, model=model, **kwargs)
    return wrapper


ReplyPost = GraphQLObjectType(
    name='ReplyPost',
    fields=lambda: {
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
        'body_markdown': GraphQLField(type=GraphQLString),
    }
)


@with_model
async def post_replies_resolver(post, info, *, model):
    return await model.list_post_replies(post.id)


Post = GraphQLObjectType(
    name='Post',
    fields=lambda: {
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
        'body_markdown': GraphQLField(type=GraphQLString),
        'replies': GraphQLField(
            type=GraphQLList(ReplyPost),
            resolver=post_replies_resolver),
    }
)


@with_model
async def conversation_posts_resolver(conversation, info, *, model):
    return await model.list_conversation_posts(conversation_id=conversation.id)


Conversation = GraphQLObjectType(
    name='Conversation',
    fields=lambda: {
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
        'posts': GraphQLField(
            type=GraphQLList(Post),
            resolver=conversation_posts_resolver),
    }
)


@with_model
async def topic_conversation_resolver(topic, info, *, model):
    return await model.get_conversation(topic.conversation_id)


@with_model
async def topic_category_resolver(topic, info, *, model):
    categories = await model.list_categories()
    categories = [cat for cat in categories if topic.id in cat.topic_ids]
    category, = categories
    return category


Topic = GraphQLObjectType(
    name='Topic',
    fields=lambda: {
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
        'title': GraphQLField(type=GraphQLString),
        'conversation': GraphQLField(
            type=Conversation,
            resolver=topic_conversation_resolver),
        'category': GraphQLField(
            type=Category,
            resolver=topic_category_resolver),
    }
)


@with_model
async def cateogory_topics_resolver(category, info, *, model):
    tasks = [
        create_task(model.get_topic(topic_id))
        for topic_id in category.topic_ids
    ]
    return [await t for t in tasks]


Category = GraphQLObjectType(
    name='Category',
    fields={
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
        'title': GraphQLField(type=GraphQLString),
        'topics': GraphQLField(
            type=GraphQLList(Topic),
            resolver=cateogory_topics_resolver),
    }
)


@with_model
async def categories_resolver(root, info, *, model):
    return await model.list_categories()


Schema = GraphQLSchema(
    query=GraphQLObjectType(
        name='RootQueryType',
        fields={
            'categories': GraphQLField(
                type=GraphQLList(Category),
                resolver=categories_resolver),
        }
    )
)
