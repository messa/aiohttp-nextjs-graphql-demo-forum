import React from 'react'
import { graphql } from 'react-relay'
import Link from 'next/link'
import PageLayout from '../components/PageLayout'
import withData from '../util/withData'

class IndexPage extends React.Component {

  render() {
    const { categories } = this.props
    return (
      <PageLayout>
        <h1>Forum</h1>
        <p>Categories:</p>
        <ul>
          {categories.edges.map(edge => edge.node).map(category => (
            <li key={category.id}>
              <Link href={`/category?id=${category.id}`} prefetch><a>{category.title}</a></Link>
            </li>
          ))}
        </ul>
      </PageLayout>
    )
  }

}

export default withData(IndexPage, {
  query: graphql`
    query pages_indexQuery {
      categories {
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
