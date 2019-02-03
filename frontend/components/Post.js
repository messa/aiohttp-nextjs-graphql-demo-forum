import React from 'react'
import { createFragmentContainer, commitMutation, graphql } from 'react-relay'
import { getRelayEnvironment } from '../util/relayEnvironment'
import ReplyButton from './ReplyButton'

const postReplyMutation = graphql`
  mutation Post_PostReplyMutation(
    $input: PostReplyInput!
  ) {
    postReply(input: $input) {
      newReplyPost {
        id
        bodyMarkdown
      }
    }
  }
`

class Post extends React.Component {

  state = {
    showReplyForm: false,
    replyText: '',
  }

  handleReplyClick = () => {
    this.setState({ showReplyForm: true, replyText: '' })
  }

  handleReplyTextChange = (event) => {
    this.setState({ replyText: event.target.value })
  }

  handleSubmitReply = () => {
    const { post } = this.props
    const { replyText } = this.state
    commitMutation(
      getRelayEnvironment(),
      {
        mutation: postReplyMutation,
        variables: { input: { postId: post.id, bodyMarkdown: replyText }},
        onCompleted: (response, errors) => {
          console.log('Response received from server.')
        },
        onError: err => console.error(err),
      },
    )
    this.setState({ showReplyForm: false, replyText: '' })
  }

  render() {
    const { showReplyForm, replyText } = this.state
    const { post, level } = this.props
    const replies = post.replies && post.replies.edges.map(edge => edge.node)
    return (
      <div className='Post'>
        <pre>{post.bodyMarkdown}</pre>
        {!showReplyForm && <ReplyButton onClick={this.handleReplyClick}>Reply</ReplyButton>}
        {showReplyForm && (
          <>
            <form>
              <textarea value={replyText} onChange={this.handleReplyTextChange} />
              <input type="button" value="Submit" onClick={this.handleSubmitReply} />
            </form>
          </>
        )}
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
