import React from "react"

const TableHeader = ({ columnLabels }) => {
  return (
    <thead>
      <tr>
        {columnLabels.map((label, i) => (
          <th
            key={i}
            className="px-6 py-3 border-b border-gray-200 bg-gray-50 text-left text-xs leading-4 font-medium text-gray-500 uppercase tracking-wider"
          >
            {label}
          </th>
        ))}
        <th className="px-6 py-3 border-b border-gray-200 bg-gray-50"></th>
      </tr>
    </thead>
  )
}

const TableRow = ({ actionUrl, data }) => {
  return (
    <tr>
      {data.map((value, i) => (
        <td
          key={i}
          className="px-6 py-4 whitespace-no-wrap border-b border-gray-200 text-sm leading-5 first:font-medium text-gray-500 first:text-gray-900"
        >
          {value}
        </td>
      ))}
      <td className="px-6 py-4 whitespace-no-wrap text-right border-b border-gray-200 text-sm leading-5 font-medium">
        <a href={actionUrl} className="text-indigo-600 hover:text-indigo-900">
          Edit
        </a>
      </td>
    </tr>
  )
}

const Table = ({ columnLabels, data }) => {
  return (
    <div className="flex flex-col">
      <div className="-my-2 py-2 overflow-x-auto sm:-mx-6 sm:px-6 lg:-mx-8 lg:px-8">
        <div className="align-middle inline-block min-w-full shadow overflow-hidden sm:rounded-lg border-b border-gray-200">
          <table className="min-w-full">
            <TableHeader columnLabels={columnLabels} />
            <tbody className="bg-white">
              {data.map((row, i) => (
                <TableRow key={i} data={row} actionUrl={`/users/${i}`} />
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Table
