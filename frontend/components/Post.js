import React from 'react'
import { createFragmentContainer, graphql } from 'react-relay'

class Post extends React.Component {

  render() {
    const { post, level } = this.props
    const replies = post.replies && post.replies.edges.map(edge => edge.node)
    return (
      <div className='Post'>
        <pre>{post.bodyMarkdown}</pre>
        {replies && replies.length > 0 && (
          <>
            <p className='f7 b'>Replies:</p>
            <div style={{ marginLeft: '2em' }}>
              {replies.map(reply => (
                <Post key={reply.id} post={reply} level={level + 1} />
              ))}
            </div>
          </>
        )}
        <style jsx>{`
          .Post:not(:first-child) {
            border-top: 1px solid black;
          }
        `}</style>
      </div>
    )
  }

}

export default createFragmentContainer(Post, {
  post: graphql`
    fragment Post_post on Post {
      id
      bodyMarkdown
      replies {
        edges {
          node {
            id
            bodyMarkdown
          }
        }
      }
    }
  `
})
