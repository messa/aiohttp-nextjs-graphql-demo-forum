import React from 'react'
import Head from 'next/head'

export default ({ children }) => (
  <div className='PageLayout pa4 avenir'>
    <Head>
      <title>Forum</title>
      <link rel="stylesheet" href="https://unpkg.com/tachyons@4/css/tachyons.min.css" />
    </Head>
    {children}
  </div>
)
