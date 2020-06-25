import React from "react"

import AppLayout from "components/layout/AppLayout"

const Dashboard = ({ userProfile, messages }) => (
  <div>
    {messages.map((message, idx) => (
      <div key={idx}>{message.message}</div>
    ))}
  </div>
)

Dashboard.layout = (page) => (
  <AppLayout children={page} title="Dashboard" section="dashboard" />
)

export default Dashboard
