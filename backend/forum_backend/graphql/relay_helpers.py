from collections import namedtuple
from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLArgument,
    GraphQLNonNull,
    GraphQLString,
    GraphQLInt,
    GraphQLList,
    GraphQLBoolean,
)


connection_args = {
    'before': GraphQLArgument(GraphQLString),
    'after': GraphQLArgument(GraphQLString),
    'first': GraphQLArgument(GraphQLInt),
    'last': GraphQLArgument(GraphQLInt),
}


def relay_connection_type(node_type):
    base_name = node_type.name
    Edge = GraphQLObjectType(
        name=base_name + 'Edge',
        fields={
            'cursor': GraphQLField(type=GraphQLNonNull(GraphQLString)),
            'node': GraphQLField(type=node_type),
        })
    Connection = GraphQLObjectType(
        name=base_name + 'Connection',
        fields={
            'pageInfo': GraphQLField(type=GraphQLNonNull(PageInfoType)),
            'edges': GraphQLField(type=GraphQLList(Edge)),
        })
    return Connection


PageInfoType = GraphQLObjectType(
    name='PageInfo',
    fields={
        'hasNextPage': GraphQLField(type=GraphQLNonNull(GraphQLBoolean)),
        'hasPreviousPage': GraphQLField(type=GraphQLNonNull(GraphQLBoolean)),
        'startCursor': GraphQLField(type=GraphQLString),
        'endCursor': GraphQLField(type=GraphQLString),
    })


ConnectionData = namedtuple('ConnectionData', 'pageInfo edges')

EdgeData = namedtuple('EdgeData', 'cursor node')


class PageInfoData:

    __slots__ = ('hasNextPage', 'hasPreviousPage', 'startCursor', 'endCursor')

    def __init__(self, has_next_page=False, has_previous_page=False, start_cursor=None, end_cursor=None):
        self.hasNextPage = bool(has_next_page)
        self.hasPreviousPage = bool(has_previous_page)
        self.startCursor = start_cursor
        self.endCursor = end_cursor


def connection_from_list(items, before=None, after=None, first=None, last=None):
    # https://facebook.github.io/relay/graphql/connections.htm
    # https://github.com/graphql/graphql-relay-js/blob/master/src/connection/arrayconnection.js
    count = len(items)
    slice_start, slice_end = 0, count
    if after is not None:
        slice_start = int(after) + 1
    if before is not None:
        slice_end = int(before)
    if first is not None:
        if first < 0:
            raise Exception('first cannot be negative')
        slice_end = min(slice_end, slice_start + first)
    if last is not None:
        if last < 0:
            raise Exception('last cannot be negative')
        slice_start = max(slice_start, slice_end - last)
    sliced_items = items[slice_start:slice_end]
    edges = [
        EdgeData(cursor=str(n), node=item)
        for n, item in enumerate(sliced_items)]
    return ConnectionData(
        edges=edges,
        pageInfo=PageInfoData(
            has_next_page=slice_end < count,
            has_previous_page=slice_start > 0,
            start_cursor=edges[0].cursor if edges else None,
            end_cursor=edges[-1].cursor if edges else None,
        ))
