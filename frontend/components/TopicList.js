import React from 'react'
import { createFragmentContainer, graphql } from 'react-relay'
import Topic from './Topic'

class TopicList extends React.Component {

  render() {
    const { category } = this.props
    return (
      <div className='TopicList'>
        {category.topics.edges.map(edge => edge.node).map(topic => (
          <Topic key={topic.id} topic={topic} />
        ))}
      </div>
    )
  }

}

export default createFragmentContainer(TopicList, {
  category: graphql`
    fragment TopicList_category on Category {
      title
      topics {
        edges {
          node {
            id
            title
            ...Topic_topic
          }
        }
      }
    }
  `
})
