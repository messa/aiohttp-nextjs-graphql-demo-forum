import React from 'react'
import { createFragmentContainer, graphql } from 'react-relay'

class TopicList extends React.Component {

  render() {
    const { category } = this.props
    return (
      <div className='TopicList'>
        <h2>Topics</h2>
        <pre>{JSON.stringify(category.topics, null, 2)}</pre>
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
          }
        }
      }
    }
  `
})
