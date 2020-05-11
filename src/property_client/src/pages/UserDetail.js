import React from "react";
import AppLayout from "components/layout/AppLayout";

const UserDetail = ({ user }) => (
  <div>
    <div>{user.id}</div>
    <div>{user.name}</div>
  </div>
);

UserDetail.layout = (page) => (
  <AppLayout children={page} title="User Profile" section="users" />
);

export default UserDetail;
