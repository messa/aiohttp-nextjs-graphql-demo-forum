import { Environment, Network, RecordSource, Store } from 'relay-runtime'
import fetch from 'isomorphic-unfetch'

const relayEndpoint = process.browser ? '/api/graphql' : (process.env.RELAY_ENDPOINT || 'http://127.0.0.1:8080/api/graphql')

// Define a function that fetches the results of an operation (query/mutation/etc)
// and returns its results as a Promise:
async function fetchQuery (operation, variables, cacheConfig, uploadables) {
  const r = await fetch(relayEndpoint, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json'
    }, // Add authentication and other headers here
    body: JSON.stringify({
      query: operation.text, // GraphQL text from input
      variables
    })
  })
  if (r.status != 200) {
    throw new Error(`POST ${relayEndpoint} failed with status ${r.status}`)
  }
  const data = await r.json()
  return data
}

let relayEnvironment = null

export function getRelayEnvironment() {
  if (!process.browser) {
    throw new Error('This is supposed to be used only in browser')
  }
  if (!relayEnvironment) {
    throw new Error('relayEnvironment not initialized')
  }
  return relayEnvironment
}

export function initRelayEnvironment ({ records = {} } = {}) {
  // Create a network layer from the fetch function
  const network = Network.create(fetchQuery)
  const store = new Store(new RecordSource(records))

  // Make sure to create a new Relay environment for every server-side request so that data
  // isn't shared between connections (which would be bad)
  if (!process.browser) {
    return new Environment({ network, store })
  }

  // reuse Relay environment on client-side
  if (!relayEnvironment) {
    relayEnvironment = new Environment({ network, store })
  }

  return relayEnvironment
}
