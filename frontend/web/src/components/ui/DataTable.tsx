#!/usr/bin/env typescript
/**
 * NEXUS Platform - DataTable Component
 * Advanced data table with sorting, filtering, pagination, and selection
 */

import React, { useState, useMemo, useCallback } from "react";
import Card from "./Card";
import Button from "./Button";
import Input from "./Input";
import Badge from "./Badge";
import LoadingSpinner from "./LoadingSpinner";
import Select from "./Select";

export interface Column<T = Record<string, unknown>> {
  key: string;
  title: string;
  dataIndex: string;
  width?: number | string;
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: unknown, record: T, index: number) => React.ReactNode;
  sorter?: (a: T, b: T) => number;
  filterType?: "text" | "select" | "date" | "number";
  filterOptions?: { label: string; value: string | number }[];
  align?: "left" | "center" | "right";
  fixed?: "left" | "right";
  ellipsis?: boolean;
}

export interface DataTableProps<T = Record<string, unknown>> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  pagination?: {
    current: number;
    pageSize: number;
    total: number;
    showSizeChanger?: boolean;
    showQuickJumper?: boolean;
    pageSizeOptions?: string[];
  };
  selection?: {
    type: "checkbox" | "radio";
    selectedRowKeys: string[];
    onChange: (selectedRowKeys: string[], selectedRows: T[]) => void;
    getCheckboxProps?: (record: T) => { disabled?: boolean };
  };
  sorting?: {
    sortField: string;
    sortOrder: "asc" | "desc" | null;
    onChange: (field: string, order: "asc" | "desc" | null) => void;
  };
  filtering?: {
    filters: Record<string, string | number | boolean>;
    onChange: (filters: Record<string, string | number | boolean>) => void;
  };
  rowKey: string | ((record: T) => string);
  onRow?: (
    record: T,
    index: number,
  ) => {
    onClick?: () => void;
    onDoubleClick?: () => void;
    className?: string;
    style?: React.CSSProperties;
  };
  emptyText?: string;
  className?: string;
  size?: "small" | "medium" | "large";
  bordered?: boolean;
  striped?: boolean;
  hoverable?: boolean;
}

export const DataTable = <T extends Record<string, any>>({
  columns,
  data,
  loading = false,
  pagination,
  selection,
  sorting,
  filtering,
  rowKey,
  onRow,
  emptyText = "No data available",
  className = "",
  size = "medium",
  bordered = false,
  striped = false,
  hoverable = true,
}: DataTableProps<T>) => {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  // Get row key
  const getRowKey = useCallback(
    (record: T, index: number): string => {
      if (typeof rowKey === "function") {
        return rowKey(record);
      }
      return record[rowKey] || index.toString();
    },
    [rowKey],
  );

  // Handle sorting
  const handleSort = useCallback(
    (column: Column<T>) => {
      if (!column.sortable || !sorting) return;

      const { sortField, sortOrder, onChange } = sorting;
      let newOrder: "asc" | "desc" | null = "asc";

      if (sortField === column.dataIndex) {
        if (sortOrder === "asc") {
          newOrder = "desc";
        } else if (sortOrder === "desc") {
          newOrder = null;
        }
      }

      onChange(column.dataIndex, newOrder);
    },
    [sorting],
  );

  // Handle selection
  const handleSelectAll = useCallback(
    (checked: boolean) => {
      if (!selection) return;

      const { onChange } = selection;
      if (checked) {
        const allKeys = data.map((record, index) => getRowKey(record, index));
        onChange(allKeys, data);
      } else {
        onChange([], []);
      }
    },
    [selection, data, getRowKey],
  );

  const handleSelectRow = useCallback(
    (record: T, index: number, checked: boolean) => {
      if (!selection) return;

      const { selectedRowKeys, onChange } = selection;
      const key = getRowKey(record, index);

      let newSelectedKeys: string[];
      if (checked) {
        newSelectedKeys = [...selectedRowKeys, key];
      } else {
        newSelectedKeys = selectedRowKeys.filter((k) => k !== key);
      }

      const newSelectedRows = data.filter((record, idx) =>
        newSelectedKeys.includes(getRowKey(record, idx)),
      );

      onChange(newSelectedKeys, newSelectedRows);
    },
    [selection, data, getRowKey],
  );

  // Check if row is selected
  const isRowSelected = useCallback(
    (record: T, index: number) => {
      if (!selection) return false;
      const key = getRowKey(record, index);
      return selection.selectedRowKeys.includes(key);
    },
    [selection, getRowKey],
  );

  // Check if all rows are selected
  const isAllSelected = useMemo(() => {
    if (!selection || data.length === 0) return false;
    return data.every((record, index) => isRowSelected(record, index));
  }, [selection, data, isRowSelected]);

  // Check if some rows are selected
  const isIndeterminate = useMemo(() => {
    if (!selection || data.length === 0) return false;
    const selectedCount = data.filter((record, index) =>
      isRowSelected(record, index),
    ).length;
    return selectedCount > 0 && selectedCount < data.length;
  }, [selection, data, isRowSelected]);

  // Get sort icon
  const getSortIcon = (column: Column<T>) => {
    if (!column.sortable || !sorting) return null;

    const { sortField, sortOrder } = sorting;
    if (sortField !== column.dataIndex) {
      return (
        <svg
          className="w-4 h-4 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
          />
        </svg>
      );
    }

    if (sortOrder === "asc") {
      return (
        <svg
          className="w-4 h-4 text-blue-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 15l7-7 7 7"
          />
        </svg>
      );
    }

    if (sortOrder === "desc") {
      return (
        <svg
          className="w-4 h-4 text-blue-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      );
    }

    return null;
  };

  // Size classes
  const sizeClasses = {
    small: "text-sm",
    medium: "text-base",
    large: "text-lg",
  };

  const paddingClasses = {
    small: "px-3 py-2",
    medium: "px-4 py-3",
    large: "px-6 py-4",
  };

  if (loading) {
    return (
      <Card className={`p-8 ${className}`}>
        <div className="flex items-center justify-center">
          <LoadingSpinner size="large" />
        </div>
      </Card>
    );
  }

  return (
    <Card className={`overflow-hidden ${className}`}>
      <div className="overflow-x-auto">
        <table className={`w-full ${sizeClasses[size]}`}>
          <thead className="bg-gray-50 dark:bg-gray-800">
            <tr>
              {selection && (
                <th className={`${paddingClasses[size]} text-left`}>
                  {selection.type === "checkbox" ? (
                    <input
                      type="checkbox"
                      checked={isAllSelected}
                      ref={(input) => {
                        if (input) input.indeterminate = isIndeterminate;
                      }}
                      onChange={(e) => handleSelectAll(e.target.checked)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  ) : null}
                </th>
              )}
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={`${paddingClasses[size]} text-${column.align || "left"} ${
                    column.sortable
                      ? "cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                      : ""
                  }`}
                  style={{ width: column.width }}
                  onClick={() => handleSort(column)}
                >
                  <div className="flex items-center space-x-2">
                    <span>{column.title}</span>
                    {getSortIcon(column)}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody
            className={`divide-y divide-gray-200 dark:divide-gray-700 ${striped ? "divide-y" : ""}`}
          >
            {data.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length + (selection ? 1 : 0)}
                  className={`${paddingClasses[size]} text-center text-gray-500 dark:text-gray-400`}
                >
                  {emptyText}
                </td>
              </tr>
            ) : (
              data.map((record, index) => {
                const key = getRowKey(record, index);
                const rowProps = onRow ? onRow(record, index) : {};
                const isSelected = isRowSelected(record, index);

                return (
                  <tr
                    key={key}
                    className={`
                      ${hoverable ? "hover:bg-gray-50 dark:hover:bg-gray-800" : ""}
                      ${isSelected ? "bg-blue-50 dark:bg-blue-900/20" : ""}
                      ${rowProps.className || ""}
                    `}
                    onClick={rowProps.onClick}
                    onDoubleClick={rowProps.onDoubleClick}
                    style={rowProps.style}
                  >
                    {selection && (
                      <td className={`${paddingClasses[size]} text-left`}>
                        <input
                          type={selection.type}
                          checked={isSelected}
                          onChange={(e) =>
                            handleSelectRow(record, index, e.target.checked)
                          }
                          disabled={
                            selection.getCheckboxProps?.(record)?.disabled
                          }
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                      </td>
                    )}
                    {columns.map((column) => {
                      const value = record[column.dataIndex];
                      const renderedValue = column.render
                        ? column.render(value, record, index)
                        : value;

                      return (
                        <td
                          key={column.key}
                          className={`${paddingClasses[size]} text-${column.align || "left"} ${
                            column.ellipsis ? "truncate" : ""
                          }`}
                          style={{ width: column.width }}
                        >
                          {renderedValue}
                        </td>
                      );
                    })}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {pagination && (
        <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Showing {(pagination.current - 1) * pagination.pageSize + 1} to{" "}
                {Math.min(
                  pagination.current * pagination.pageSize,
                  pagination.total,
                )}{" "}
                of {pagination.total} entries
              </span>
            </div>
            <div className="flex items-center space-x-2">
              {pagination.showSizeChanger && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Show:
                  </span>
                  <Select
                    label="Page Size"
                    value={pagination.pageSize.toString()}
                    onChange={(value) => {
                      // Handle page size change
                      console.log("Page size changed to:", value);
                    }}
                    options={
                      pagination.pageSizeOptions?.map((size) => ({
                        label: size,
                        value: size,
                      })) || []
                    }
                  />
                </div>
              )}
              <div className="flex items-center space-x-1">
                <Button
                  size="small"
                  variant="outlined"
                  disabled={pagination.current === 1}
                  onClick={() => {
                    // Handle previous page
                    console.log("Previous page");
                  }}
                >
                  Previous
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  disabled={
                    pagination.current * pagination.pageSize >= pagination.total
                  }
                  onClick={() => {
                    // Handle next page
                    console.log("Next page");
                  }}
                >
                  Next
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
};

export default DataTable;
