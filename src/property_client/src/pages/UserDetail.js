import React from "react";

const UserDetail = ({ user }) => (
  <div>
    <div>{user.id}</div>
    <div>{user.name}</div>
  </div>
);

export default UserDetail;
