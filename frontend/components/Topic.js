import React from 'react'
import { createRefetchContainer, graphql } from 'react-relay'
import Conversation from './Conversation'

class Topic extends React.Component {

  refetch = () => {
    console.info('Topic.refetch')
    const { relay, topic } = this.props
    relay.refetch(
      { topicId: topic.id },
      null,
      () => { console.log('Refetch done') },
      { force: true }
    )
  }

  render() {
    const { topic } = this.props
    return (
      <div className='Topic'>
        <h2 className='topicTitle'>{topic.title} <span className='id'>({topic.id})</span></h2>
        <Conversation conversation={topic.conversation} refetchTopic={this.refetch} />
        <style jsx>{`
          .topicTitle .id {
            font-weight: 400;
            font-size: 70%;
            color: #999;
            font-family: monospace;
          }
        `}</style>
      </div>
    )
  }

}

export default createRefetchContainer(
  Topic,
  {
    topic: graphql`
      fragment Topic_topic on Topic {
        id
        title
        conversation {
          ...Conversation_conversation
        }
      }
    `
  },
  graphql`
    query TopicRefetchQuery($topicId: ID!) {
      topic: node(id: $topicId) {
        ...on Topic {
          id
          title
          conversation {
            ...Conversation_conversation
          }
        }
      }
    }
  `)
