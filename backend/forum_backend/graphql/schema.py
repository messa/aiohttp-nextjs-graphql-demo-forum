from asyncio import create_task
from functools import wraps
from inspect import iscoroutinefunction
from graphql import (
    graphql,
    GraphQLSchema,
    GraphQLInterfaceType,
    GraphQLObjectType,
    GraphQLField,
    GraphQLNonNull,
    GraphQLString,
    GraphQLList,
    GraphQLID,
    GraphQLBoolean,
)


def with_model(f):
    '''
    Decorator for passing model to resolver functions
    '''
    assert iscoroutinefunction(f)
    async def wrapper(parent, info, *args, **kwargs):
        assert 'model' not in kwargs
        model = info.context['request'].app['model']
        return await f(parent, info, *args, model=model, **kwargs)
    return wrapper


def resolve_node_type(value):
    # See also: https://stackoverflow.com/q/34726666/196206
    raise Exception('NIY')


NodeInterface = GraphQLInterfaceType(
    name='Node',
    fields={
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
    },
    resolve_type=resolve_node_type)


PageInfo = GraphQLObjectType(
    name='PageInfo',
    fields={
        'hasNextPage': GraphQLField(type=GraphQLNonNull(GraphQLBoolean)),
        'hasPreviousPage': GraphQLField(type=GraphQLNonNull(GraphQLBoolean)),
        'startCursor': GraphQLField(type=GraphQLString),
        'endCursor': GraphQLField(type=GraphQLString),
    })


ReplyPost = GraphQLObjectType(
    name='ReplyPost',
    interfaces=[NodeInterface],
    fields=lambda: {
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
        'body_markdown': GraphQLField(type=GraphQLString),
    })


ReplyPostEdge = GraphQLObjectType(
    name='ReplyPostEdge',
    fields={
        'cursor': GraphQLField(type=GraphQLNonNull(GraphQLString)),
        'node': GraphQLField(type=ReplyPost),
    })


ReplyPostConnection = GraphQLObjectType(
    name='ReplyPostConnection',
    fields={
        'pageInfo': GraphQLField(type=GraphQLNonNull(PageInfo)),
        'edges': GraphQLField(type=GraphQLList(ReplyPostEdge)),
    })


@with_model
async def post_replies_resolver(post, info, *, model):
    return await model.list_post_replies(post.id)


Post = GraphQLObjectType(
    name='Post',
    interfaces=[NodeInterface],
    fields=lambda: {
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
        'body_markdown': GraphQLField(type=GraphQLString),
        'replies': GraphQLField(
            type=ReplyPostConnection,
            resolver=post_replies_resolver),
    })


PostEdge = GraphQLObjectType(
    name='PostEdge',
    fields={
        'cursor': GraphQLField(type=GraphQLNonNull(GraphQLString)),
        'node': GraphQLField(type=Post),
    })


PostConnection = GraphQLObjectType(
    name='PostConnection',
    fields={
        'pageInfo': GraphQLField(type=GraphQLNonNull(PageInfo)),
        'edges': GraphQLField(type=GraphQLList(PostEdge)),
    })


@with_model
async def conversation_posts_resolver(conversation, info, *, model):
    return await model.list_conversation_posts(conversation_id=conversation.id)


Conversation = GraphQLObjectType(
    name='Conversation',
    interfaces=[NodeInterface],
    fields=lambda: {
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
        'posts': GraphQLField(
            type=PostConnection,
            resolver=conversation_posts_resolver),
    })


ConversationEdge = GraphQLObjectType(
    name='ConversationEdge',
    fields={
        'cursor': GraphQLField(type=GraphQLNonNull(GraphQLString)),
        'node': GraphQLField(type=Conversation),
    })


ConversationConnection = GraphQLObjectType(
    name='ConversationConnection',
    fields={
        'pageInfo': GraphQLField(type=GraphQLNonNull(PageInfo)),
        'edges': GraphQLField(type=GraphQLList(ConversationEdge)),
    })


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


TopicEdge = GraphQLObjectType(
    name='TopicEdge',
    fields={
        'cursor': GraphQLField(type=GraphQLNonNull(GraphQLString)),
        'node': GraphQLField(type=Topic),
    })


TopicConnection = GraphQLObjectType(
    name='TopicConnection',
    fields={
        'pageInfo': GraphQLField(type=GraphQLNonNull(PageInfo)),
        'edges': GraphQLField(type=GraphQLList(TopicEdge)),
    })


@with_model
async def cateogory_topics_resolver(category, info, *, model):
    tasks = [
        create_task(model.get_topic(topic_id))
        for topic_id in category.topic_ids
    ]
    return [await t for t in tasks]


Category = GraphQLObjectType(
    name='Category',
    interfaces=[NodeInterface],
    fields={
        'id': GraphQLField(type=GraphQLNonNull(GraphQLID)),
        'title': GraphQLField(type=GraphQLString),
        'topics': GraphQLField(
            type=TopicConnection,
            resolver=cateogory_topics_resolver),
    })


async def node_resolver(root, info):
    raise Exception('NIY')


@with_model
async def categories_resolver(root, info, *, model):
    return await model.list_categories()


Schema = GraphQLSchema(
    query=GraphQLObjectType(
        name='RootQueryType',
        fields={
            'node': GraphQLField(
                type=NodeInterface,
                resolver=node_resolver),
            'categories': GraphQLField(
                type=GraphQLList(Category),
                resolver=categories_resolver),
        }
    ))
