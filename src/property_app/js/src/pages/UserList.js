import React from "react";
import AppLayout from "components/layout/AppLayout";
import Table from "components/Table";

const UserList = ({ users }) => {
  return (
    <Table
      columnLabels={["Name", "Title", "Email", "Role"]}
      data={users.map((user) => [user.name, "Owner", "test@testuser.com", "Admin"])}
    />
  );
};

UserList.layout = (page) => <AppLayout children={page} title="Users" section="users" />;

export default UserList;
