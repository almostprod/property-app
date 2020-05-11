import React from "react";
import DefaultLayout from "../components/layout/DefaultLayout";

const UserDetail = ({ user }) => (
  <div>
    <div>{user.id}</div>
    <div>{user.name}</div>
  </div>
);

UserDetail.layout = (page) => (
  <DefaultLayout children={page} title="User Profile" section="users" />
);

export default UserDetail;
