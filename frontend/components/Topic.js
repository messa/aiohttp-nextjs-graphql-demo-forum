import React from 'react'
import { createFragmentContainer, graphql } from 'react-relay'
import Conversation from './Conversation'

class Topic extends React.Component {

  render() {
    const { topic } = this.props
    return (
      <div className='Topic'>
        <h2>{topic.title}</h2>
        <Conversation conversation={topic.conversation} />
      </div>
    )
  }

}

export default createFragmentContainer(Topic, {
  topic: graphql`
    fragment Topic_topic on Topic {
      title
      conversation {
        ...Conversation_conversation
      }
    }
  `
})
