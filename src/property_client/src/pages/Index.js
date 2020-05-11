import React from "react";

import DefaultLayout from "../components/layout/DefaultLayout";

const Index = ({ pageContent }) => <div>{pageContent}</div>;

Index.layout = (page) => (
  <DefaultLayout children={page} title="Index" section="dashboard" />
);

export default Index;
