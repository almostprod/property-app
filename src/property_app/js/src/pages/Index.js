import React from "react";

import AppLayout from "components/layout/AppLayout";

const Index = ({ pageContent }) => <div>{pageContent}</div>;

Index.layout = (page) => (
  <AppLayout children={page} title="Index" section="dashboard" />
);

export default Index;
