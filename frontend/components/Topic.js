import React from 'react'
import { createRefetchContainer, graphql, requestSubscription } from 'react-relay'
import { getRelayEnvironment } from '../util/relayEnvironment'
import Conversation from './Conversation'

class Topic extends React.Component {

  componentDidMount() {
    const { topic } = this.props
    this.relaySubscription = requestSubscription(
      getRelayEnvironment(),
      {
        subscription: graphql`
          subscription Topic_ConversationUpdatedSubscription($conversationId: ID!) {
            conversationUpdated(conversationId: $conversationId) {
              id
            }
          }
        `,
        variables: { conversationId: topic.conversation.id },
        onCompleted: () => console.info('subscription completed'),
        onError: (err) => console.error(err),
        onNext: (response) => {
          console.info('subscription onNext:', response)
          this.refetch()
        },
      }
    )
  }

  componentWillUnmount() {
    if (this.relaySubscription) {
      try {
        this.relaySubscription.dispose()
      } catch (err) {
        console.error('Failed to dispose relaySubscription in componentWillUnmount:', err)
      }
      this.relaySubscription = null
    }
  }

  refetch = () => {
    if (this.refetchInProgress) {
      console.debug('Topic refetch already in progress')
      return
    }
    console.debug('Topic refetch')
    const { relay, topic } = this.props
    this.refetchInProgress = true
    relay.refetch(
      { topicId: topic.id },
      null,
      () => {
        console.debug('Refetch done')
        this.refetchInProgress = false
      },
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
          id
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
            id
            ...Conversation_conversation
          }
        }
      }
    }
  `)
