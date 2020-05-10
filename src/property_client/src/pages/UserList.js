import React from "react";
import { InertiaLink as Link } from "@inertiajs/inertia-react";

const UserList = ({ users }) => (
  <div>
    <ul>
      {users.map((user) => (
        <li>
          <Link href={`/users/${user.id}`}>{user.name}</Link>
        </li>
      ))}
    </ul>
  </div>
);

export default UserList;
