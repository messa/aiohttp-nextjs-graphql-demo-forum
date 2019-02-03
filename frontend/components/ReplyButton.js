import React from 'react'

export default ({ children, onClick }) => (
  <button className="f6 link dim br3 ba ph3 pv2 mb2 dib black" style={{ cursor: 'pointer' }} onClick={onClick}>
    {children}
  </button>
)
