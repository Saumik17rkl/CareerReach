import React from 'react';

export default function EmptyState({ message }) {
  return <div className="mt-10 rounded-xl border border-dashed border-slate-300 p-8 text-center text-slate-500 dark:border-slate-700 dark:text-slate-400">{message}</div>;
}
