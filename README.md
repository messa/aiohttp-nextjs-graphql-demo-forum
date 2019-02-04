Forum web app using aiohttp, Next.js and GraphQL
================================================

**Frontend component:** visualizes data fetched from the backend

- [React](https://reactjs.org/)
- [Next.js](https://nextjs.org/)
- [Relay Modern](http://facebook.github.io/relay/docs/en/introduction-to-relay.html)

**Backend component:** manages data, authentication (not implemented yet), cookies, websockets

- [Python](https://www.python.org/)
- [aiohttp](https://aiohttp.readthedocs.io/en/stable/)
- [Graphene](https://graphene-python.org/)
  - [aiohttp-graphql](https://github.com/graphql-python/aiohttp-graphql)
  - [graphql-core-next](https://github.com/graphql-python/graphql-core-next)
- [Requests-OAuthlib](https://requests-oauthlib.readthedocs.io/en/latest/)

Routing:

                          /api/*
                          /auth/*
                        +-----------------> backend (aiohttp)  <--+
                        |                                         | server-side
    --> load balancer --+                                         | render (SSR)
       (nginx, ...)     | /* (the rest)                           | data fetch
                        +-----------------> frontend (Next.js) ---+
