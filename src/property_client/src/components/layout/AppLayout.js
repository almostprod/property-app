import React, { useEffect } from "react";

import NavBar from "components/NavBar.js";

const AppLayout = ({ title, section, children }) => {
  useEffect(() => {
    document.title = title;
  }, [title]);

  return (
    <div className="min-h-screen bg-white">
      <NavBar section={section} />
      <div className="py-10">
        <header>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold leading-tight text-gray-900">{title}</h1>
          </div>
        </header>
        <main>
          <div className="max-w-7xl mx-auto mt-4 px-4 sm:px-6 lg:px-8">{children}</div>
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
