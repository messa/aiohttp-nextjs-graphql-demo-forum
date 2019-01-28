import React from 'react'
import { createFragmentContainer, graphql } from 'react-relay'
import Post from './Post'

class Conversation extends React.Component {

  render() {
    const { conversation } = this.props
    return (
      <div className='Conversation'>
        {conversation.posts.edges.map(edge => edge.node).map(post => (
          <Post key={post.id} post={post} level={0} />
        ))}
        <style jsx>{`
          .Conversation {
            border-left: 1px dotted black;
            padding-left: 1em;
          }
        `}</style>
      </div>
    )
  }

}

export default createFragmentContainer(Conversation, {
  conversation: graphql`
    fragment Conversation_conversation on Conversation {
      posts {
        edges {
          node {
            id
            ...Post_post
          }
        }
      }
    }
  `
})
