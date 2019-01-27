from asyncio import create_task, gather
from collections import namedtuple
from functools import wraps
from inspect import iscoroutinefunction
import logging
from graphql import (
    graphql,
    GraphQLSchema,
    GraphQLInterfaceType,
    GraphQLObjectType,
    GraphQLField,
    GraphQLArgument,
    GraphQLNonNull,
    GraphQLString,
    GraphQLInt,
    GraphQLList,
    GraphQLID,
    GraphQLBoolean,
)

from .relay_helpers import connection_args, connection_from_list, relay_connection_type

'''
There is project github.com/graphql-python/graphql-relay-py but right now it
is somewhat outdated, so we use our own implementation of Relay connection
helpers.
'''


logger = logging.getLogger(__name__)


def with_model(f):
    '''
    Decorator for passing model to resolver functions
    '''
    assert iscoroutinefunction(f)
    async def wrapper(parent, info, *args, **kwargs):
        assert 'model' not in kwargs
        model = info.context['request'].app['model']
        return await f(parent, info, model, *args, **kwargs)
    return wrapper


def resolve_node_type(obj, info):
    # See also: https://stackoverflow.com/q/34726666/196206
    if obj.node_type == 'Post':
        return Post
    if obj.node_type == 'Category':
        return Category
    raise Exception(f'Unknown node type: {obj!r}')


NodeInterface = GraphQLInterfaceType(
    name='Node',
    fields={
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
    },
    resolve_type=resolve_node_type)


ReplyPost = GraphQLObjectType(
    name='ReplyPost',
    interfaces=[NodeInterface],
    fields=lambda: {
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
        'body_markdown': GraphQLField(type=GraphQLString),
    })


ReplyPostConnection = relay_connection_type(ReplyPost)

@with_model
async def post_replies_resolver(post, info, model, **kwargs):
    replies = await model.list_post_replies(post.id)
    return connection_from_list(replies, **kwargs)


Post = GraphQLObjectType(
    name='Post',
    interfaces=[NodeInterface],
    fields=lambda: {
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
        'body_markdown': GraphQLField(type=GraphQLString),
        'replies': GraphQLField(
            type=ReplyPostConnection,
            args=connection_args,
            resolver=post_replies_resolver),
    })


PostConnection = relay_connection_type(Post)


@with_model
async def conversation_posts_resolver(conversation, info, model, **kwargs):
    posts = await model.list_conversation_posts(conversation_id=conversation.id)
    return connection_from_list(posts, **kwargs)


Conversation = GraphQLObjectType(
    name='Conversation',
    interfaces=[NodeInterface],
    fields=lambda: {
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
        'posts': GraphQLField(
            type=PostConnection,
            args=connection_args,
            resolver=conversation_posts_resolver),
    })


ConversationConnection = relay_connection_type(Conversation)


@with_model
async def topic_conversation_resolver(topic, info, model):
    return await model.get_conversation(topic.conversation_id)


@with_model
async def topic_category_resolver(topic, info, model):
    categories = await model.list_categories()
    categories = [cat for cat in categories if topic.id in cat.topic_ids]
    category, = categories
    return category


Topic = GraphQLObjectType(
    name='Topic',
    interfaces=[NodeInterface],
    fields=lambda: {
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
        'title': GraphQLField(type=GraphQLString),
        'conversation': GraphQLField(
            type=Conversation,
            resolver=topic_conversation_resolver),
        'category': GraphQLField(
            type=Category,
            resolver=topic_category_resolver),
    })


TopicConnection = relay_connection_type(Topic)


@with_model
async def category_topics_resolver(category, info, model, **kwargs):
    return connection_from_list(await gather(*(
        model.get_topic(topic_id) for topic_id in category.topic_ids)),
        **kwargs)


Category = GraphQLObjectType(
    name='Category',
    interfaces=[NodeInterface],
    fields={
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
        'title': GraphQLField(type=GraphQLString),
        'topics': GraphQLField(
            type=TopicConnection,
            resolver=category_topics_resolver),
    })


CategoryConnection = relay_connection_type(Category)


@with_model
async def node_resolver(root, info, model, id):
    obj = await model.get_by_id(id)
    logger.debug('node_resolver %r -> %r', id, obj)
    return obj


@with_model
async def categories_resolver(root, info, model, **kwargs):
    return connection_from_list(await model.list_categories(), **kwargs)


Schema = GraphQLSchema(
    query=GraphQLObjectType(
        name='RootQueryType',
        fields={
            'node': GraphQLField(
                type=NodeInterface,
                args={
                    'id': GraphQLArgument(GraphQLNonNull(GraphQLID)),
                },
                resolver=node_resolver),
            'categories': GraphQLField(
                type=CategoryConnection,
                args=connection_args,
                resolver=categories_resolver),
        }
    ))
