import React from 'react'
import { graphql } from 'react-relay'
import Link from 'next/link'
import PageLayout from '../components/PageLayout'
import withData from '../util/withData'

class CategoryPage extends React.Component {

  render() {
    console.debug(this.props)
    const category = this.props.node
    return (
      <PageLayout>
        <p><Link href='/'><a>Back to homepage</a></Link></p>
        <h1 className='mt0 mb1'>{category.title}</h1>
        <p className='mt0 black-50 f6'>Category</p>
      </PageLayout>
    )
  }

}

export default withData(CategoryPage, {
  variables: ({ query }) => ({ categoryId: query.id }),
  query: graphql`
    query categoryQuery($categoryId: ID!) {
      node(id: $categoryId) {
        id
        ...on Category {
          title
        }
      }
    }
  `
})
