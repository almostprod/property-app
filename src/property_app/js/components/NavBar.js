import React, { useState } from "react"
import { InertiaLink as Link } from "@inertiajs/inertia-react"

import TailwindTransition from "components/TailwindTransition.js"
import PlaceholderIcon from "components/PlaceholderIcon.js"
import useComponentVisible from "hooks/use-component-visible.js"

const MobileMenuButton = ({ isOpen, onClick }) => (
  <button
    className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:bg-gray-100 focus:text-gray-500 transition duration-150 ease-in-out"
    aria-label="Main menu"
    aria-expanded="false"
    onClick={onClick}
  >
    <svg
      className={isOpen ? "hidden h-6 w-6" : "block h-6 w-6"}
      stroke="currentColor"
      fill="none"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        d="M4 6h16M4 12h16M4 18h16"
      />
    </svg>
    <svg
      className={isOpen ? "block h-6 w-6" : "hidden h-6 w-6"}
      stroke="currentColor"
      fill="none"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        d="M6 18L18 6M6 6l12 12"
      />
    </svg>
  </button>
)

const ProfileDropdown = ({}) => {
  const { ref, isComponentVisible, setIsComponentVisible } = useComponentVisible(false)

  return (
    <div className="ml-3 relative">
      <div>
        <button
          className="flex text-sm border-2 border-transparent rounded-full focus:outline-none focus:border-gray-300 transition duration-150 ease-in-out"
          id="user-menu"
          aria-label="User menu"
          aria-haspopup="true"
          onClick={() => setIsComponentVisible(!isComponentVisible)}
        >
          <PlaceholderIcon />
        </button>
      </div>
      <ProfileDropdownPanel ref={ref} showPanel={isComponentVisible} />
    </div>
  )
}

const ProfileDropdownPanel = React.forwardRef(({ showPanel }, ref) => (
  <TailwindTransition
    show={showPanel}
    enter="transition ease-out duration-200"
    enterFrom="transform opacity-0 scale-95"
    enterTo="transform opacity-100 scale-100"
    leave="transition ease-in duration-75"
    leaveFrom="transform opacity-100 scale-100"
    leaveTo="transform opacity-0 scale-95"
  >
    <div
      ref={ref}
      className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg"
    >
      {/* <!--
            Profile dropdown panel, show/hide based on dropdown state.

            Entering: "transition ease-out duration-200"
              From: "transform opacity-0 scale-95"
              To: "transform opacity-100 scale-100"
            Leaving: "transition ease-in duration-75"
              From: "transform opacity-100 scale-100"
              To: "transform opacity-0 scale-95"
          --> */}
      <div
        className="py-1 rounded-md bg-white shadow-xs"
        role="menu"
        aria-orientation="vertical"
        aria-labelledby="user-menu"
      >
        <a
          href="#"
          className="block px-4 py-2 text-sm leading-5 text-gray-700 hover:bg-gray-100 focus:outline-none focus:bg-gray-100 transition duration-150 ease-in-out"
        >
          Your Profile
        </a>
        <a
          href="#"
          className="block px-4 py-2 text-sm leading-5 text-gray-700 hover:bg-gray-100 focus:outline-none focus:bg-gray-100 transition duration-150 ease-in-out"
        >
          Settings
        </a>
        <a
          href="#"
          className="block px-4 py-2 text-sm leading-5 text-gray-700 hover:bg-gray-100 focus:outline-none focus:bg-gray-100 transition duration-150 ease-in-out"
        >
          Sign out
        </a>
      </div>
    </div>
  </TailwindTransition>
))

const Menu = ({ section }) => {
  const classNames = {
    common: [
      "inline-flex",
      "items-center",
      "px-1",
      "pt-1",
      "border-b-2",
      "text-sm",
      "font-medium",
      "leading-5",
      "focus:outline-none",
      "transition",
      "duration-150",
      "ease-in-out",
    ],
    onlyActive: ["border-indigo-500", "text-gray-900", "focus:border-indigo-700"],
    onlyNormal: [
      "border-transparent",
      "text-gray-500",
      "hover:text-gray-700",
      "hover:border-gray-300",
      "focus:text-gray-700",
      "focus:border-gray-300",
    ],
  }

  const dashboardActive = section === "dashboard"
  const usersActive = section === "users"

  const activeClasses =
    classNames.common.join(" ") + " " + classNames.onlyActive.join(" ")

  const normalClasses =
    classNames.common.join(" ") + " " + classNames.onlyNormal.join(" ")

  return (
    <div className="hidden sm:ml-6 sm:flex">
      <Link href="/" className={`${dashboardActive ? activeClasses : normalClasses}`}>
        Dashboard
      </Link>
      <Link
        href="/users"
        className={`${usersActive ? activeClasses : normalClasses} ml-8`}
      >
        Users
      </Link>
    </div>
  )
}

const MobileMenu = ({ isOpen, section }) => {
  const classNames = {
    common: [
      "block",
      "pl-3",
      "pr-4",
      "py-2",
      "border-l-4",
      "text-base",
      "font-medium",
      "focus:outline-none",
      "transition",
      "duration-150",
      "ease-in-out",
    ],
    onlyActive: [
      "border-indigo-500",
      "text-indigo-700",
      "bg-indigo-50",
      "focus:text-indigo-800",
      "focus:bg-indigo-100",
      "focus:border-indigo-700",
    ],
    onlyNormal: [
      "border-transparent",
      "text-gray-600",
      "hover:text-gray-800",
      "hover:bg-gray-50",
      "hover:border-gray-300",
      "focus:text-gray-800",
      "focus:bg-gray-50",
      "focus:border-gray-300",
    ],
  }

  const dashboardActive = section === "dashboard"
  const usersActive = section === "users"

  const activeClasses =
    classNames.common.join(" ") + " " + classNames.onlyActive.join(" ")

  const normalClasses =
    classNames.common.join(" ") + " " + classNames.onlyNormal.join(" ")

  const toggleClass = isOpen ? "block" : "hidden"

  return (
    <div className={`${toggleClass} sm:hidden`}>
      <div className="pt-2 pb-4">
        <Link href="/" className={dashboardActive ? activeClasses : normalClasses}>
          Dashboard
        </Link>
        <Link
          href="/users"
          className={`${usersActive ? activeClasses : normalClasses} mt-1`}
        >
          Users
        </Link>
      </div>
    </div>
  )
}

const NavBar = ({ section }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <>
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-2 sm:px-6 lg:px-8">
          <div className="relative flex justify-between h-16">
            <div className="absolute inset-y-0 left-0 flex items-center sm:hidden">
              <MobileMenuButton
                isOpen={isMenuOpen}
                onClick={() => setIsMenuOpen(!isMenuOpen)}
              />
            </div>
            <div className="flex-1 flex items-center justify-center sm:items-stretch sm:justify-start">
              <div className="flex-shrink-0 flex items-center">
                <img
                  className="block lg:hidden h-8 w-auto"
                  src="/static/home-solid.svg"
                  alt="Workflow logo"
                />
                <img
                  className="hidden lg:block h-8 w-auto"
                  src="/static/home-solid.svg"
                  alt="Workflow logo"
                />
              </div>
              <Menu section={section} />
            </div>
            <div className="absolute inset-y-0 right-0 flex items-center pr-2 sm:static sm:inset-auto sm:ml-6 sm:pr-0">
              <button
                className="p-1 border-2 border-transparent text-gray-400 rounded-full hover:text-gray-500 focus:outline-none focus:text-gray-500 focus:bg-gray-100 transition duration-150 ease-in-out"
                aria-label="Notifications"
              >
                <svg
                  className="h-6 w-6"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                  />
                </svg>
              </button>
              <ProfileDropdown />
            </div>
          </div>
        </div>

        <MobileMenu isOpen={isMenuOpen} section={section} />
      </nav>
    </>
  )
}

export default NavBar
