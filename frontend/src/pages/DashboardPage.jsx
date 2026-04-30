import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchSheets } from '../api';
import Loader from '../components/Loader';
import EmptyState from '../components/EmptyState';

export default function DashboardPage() {
  const [sheets, setSheets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchSheets();
        setSheets(data.sheets || []);
      } catch (err) {
        setError('Failed to load sheets. Please retry in a few moments.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <Loader />;
  if (error) return <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-200">{error}</div>;
  if (!sheets.length) return <EmptyState message="No sheets available yet." />;

  return (
    <section>
      <h1 className="mb-5 text-2xl font-semibold">Available Contact Sheets</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {sheets.map((sheet) => (
          <Link
            key={sheet}
            to={`/sheet/${encodeURIComponent(sheet)}`}
            className="group rounded-xl border border-slate-200 bg-white p-5 shadow-sm hover:-translate-y-0.5 hover:shadow-md dark:border-slate-700 dark:bg-slate-900"
          >
            <h2 className="text-lg font-semibold group-hover:text-indigo-600 dark:group-hover:text-indigo-400">{sheet}</h2>
            <p className="mt-1 text-sm text-slate-500">View recruiter contact intelligence</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
