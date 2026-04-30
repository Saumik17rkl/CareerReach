import React, { useMemo, useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchContactById, fetchContactsBySheet } from '../api';
import Loader from '../components/Loader';
import EmptyState from '../components/EmptyState';

const PAGE_SIZE = 20;

function LabeledValue({ label, value, highlight }) {
  if (!value) return null;
  return (
    <div>
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className={highlight ? 'font-medium text-indigo-600 dark:text-indigo-400' : 'font-medium'}>{value}</p>
    </div>
  );
}

export default function ContactsPage() {
  const { sheetName } = useParams();
  const sheet = decodeURIComponent(sheetName || '');
  const [contacts, setContacts] = useState([]);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [modalLoading, setModalLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await fetchContactsBySheet(sheet);
        setContacts(data.contacts || []);
      } catch {
        setError('Failed to load contacts for this sheet.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [sheet]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return contacts;
    return contacts.filter((c) => [c.company, c.name, c.hr_name].filter(Boolean).some((v) => String(v).toLowerCase().includes(q)));
  }, [contacts, search]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const paged = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  useEffect(() => setPage(1), [search, sheet]);

  const openDetails = async (id) => {
    setModalLoading(true);
    try {
      const data = await fetchContactById(id);
      setSelected(data);
    } finally {
      setModalLoading(false);
    }
  };

  const copyText = async (text) => {
    if (!text) return;
    await navigator.clipboard.writeText(text);
  };

  if (loading) return <Loader />;
  if (error) return <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-200">{error}</div>;

  return (
    <section>
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">{sheet}</h1>
          <Link to="/" className="text-sm text-indigo-600 hover:underline dark:text-indigo-400">← Back to dashboard</Link>
        </div>
        <input
          placeholder="Search by company or HR name"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 sm:max-w-sm dark:border-slate-700 dark:bg-slate-900"
        />
      </div>

      {!filtered.length ? <EmptyState message="No contacts found for this sheet/search." /> : (
        <>
          <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700">
            <table className="min-w-full bg-white text-sm dark:bg-slate-900">
              <thead className="bg-slate-100 dark:bg-slate-800">
                <tr>
                  {['Company','HR Name','Email','Mobile','Landline','Role','Location'].map((h) => <th key={h} className="px-3 py-2 text-left font-semibold">{h}</th>)}
                </tr>
              </thead>
              <tbody>
                {paged.map((c) => (
                  <tr key={c.id} className="cursor-pointer border-t border-slate-100 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/70" onClick={() => openDetails(c.id)}>
                    <td className="px-3 py-2">{c.company || '—'}</td>
                    <td className="px-3 py-2">{c.name || c.hr_name || '—'}</td>
                    <td className="px-3 py-2 text-indigo-600 dark:text-indigo-400">{c.email || '—'}</td>
                    <td className="px-3 py-2 text-indigo-600 dark:text-indigo-400">{c.mobile || '—'}</td>
                    <td className="px-3 py-2">{c.landline || '—'}</td>
                    <td className="px-3 py-2">{c.role || '—'}</td>
                    <td className="px-3 py-2">{c.location || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 flex items-center justify-end gap-2">
            <button disabled={page === 1} onClick={() => setPage((p) => Math.max(1, p - 1))} className="rounded border px-3 py-1 disabled:opacity-40">Prev</button>
            <span className="text-sm">Page {page} / {totalPages}</span>
            <button disabled={page === totalPages} onClick={() => setPage((p) => Math.min(totalPages, p + 1))} className="rounded border px-3 py-1 disabled:opacity-40">Next</button>
          </div>
        </>
      )}

      {(modalLoading || selected) && (
        <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/50 p-4" onClick={() => setSelected(null)}>
          <div className="w-full max-w-xl rounded-xl bg-white p-6 dark:bg-slate-900" onClick={(e) => e.stopPropagation()}>
            {modalLoading ? <Loader /> : (
              <>
                <h2 className="mb-4 text-xl font-semibold">Contact Details</h2>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <LabeledValue label="Company" value={selected.company} />
                  <LabeledValue label="HR Name" value={selected.name || selected.hr_name} />
                  <LabeledValue label="Role" value={selected.role} />
                  <LabeledValue label="Location" value={selected.location} />
                  <div>
                    <LabeledValue label="Email" value={selected.email} highlight />
                    {selected.email && <button onClick={() => copyText(selected.email)} className="mt-1 text-xs text-indigo-600 hover:underline">Copy email</button>}
                  </div>
                  <div>
                    <LabeledValue label="Mobile" value={selected.mobile} highlight />
                    {selected.mobile && <button onClick={() => copyText(selected.mobile)} className="mt-1 mr-3 text-xs text-indigo-600 hover:underline">Copy mobile</button>}
                    <LabeledValue label="Landline" value={selected.landline} highlight />
                    {selected.landline && <button onClick={() => copyText(selected.landline)} className="mt-1 text-xs text-indigo-600 hover:underline">Copy landline</button>}
                  </div>
                </div>
                <button onClick={() => setSelected(null)} className="mt-6 rounded-lg bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-500">Close</button>
              </>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
