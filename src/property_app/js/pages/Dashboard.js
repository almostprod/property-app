import React from "react"

import AppLayout from "components/layout/AppLayout"

const Dashboard = ({ userProfile }) => <div>{userProfile.username}</div>

Dashboard.layout = (page) => (
  <AppLayout children={page} title="Dashboard" section="dashboard" />
)

export default Dashboard
