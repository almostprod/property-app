import React from "react";
import { InertiaLink as Link } from "@inertiajs/inertia-react";

import DefaultLayout from "../components/layout/DefaultLayout";

const UserList = ({ users }) => (
  <div>
    <ul>
      {users.map((user) => (
        <li key={user.id}>
          <Link href={`/users/${user.id}`}>{user.name}</Link>
        </li>
      ))}
    </ul>
  </div>
);

UserList.layout = (page) => (
  <DefaultLayout children={page} title="Users" section="users" />
);

export default UserList;
