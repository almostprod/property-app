import React from "react";
import { InertiaLink as Link } from "@inertiajs/inertia-react";

const Index = ({ pageContent }) => (
  <div>
    <div>{pageContent || "Index"}</div>
    <div>
      <Link href="/users">Users</Link>
    </div>
  </div>
);

export default Index;
