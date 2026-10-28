import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Search, ExternalLink, ArrowLeft, Layers, CheckCircle2, ChevronLeft, ChevronRight } from 'lucide-react';
import { api } from '../services/api';
import { CrawledPage, Audit } from '../types/api';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

export const CrawledPagesPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [pages, setPages] = useState<CrawledPage[]>([]);
  const [audit, setAudit] = useState<Audit | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Pagination & Filtering
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    if (id) {
      loadPages();
    }
  }, [id, currentPage, statusFilter, search]);

  const loadPages = async () => {
    if (!id) return;
    try {
      setLoading(true);
      setError(null);

      const [pData, aData] = await Promise.all([
        api.getCrawledPages(id, {
          page: currentPage,
          limit: 15,
          status_filter: statusFilter || undefined,
          search: search || undefined,
        }),
        audit ? Promise.resolve(audit) : api.getAudit(id),
      ]);

      setPages(pData.items);
      setTotalPages(pData.pages);
      setTotalCount(pData.total);
      setAudit(aData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch crawled pages');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <Link
            to={`/audits/${id}`}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Back to Audit Results
          </Link>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Discovered & Crawled URLs ({totalCount})
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Target: <span className="font-mono font-semibold">{audit?.normalized_domain}</span>
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-3 text-xs">
          <div className="relative min-w-[220px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Filter by URL or Title..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="px-3 py-2 border border-slate-300 rounded-lg bg-white text-xs font-medium focus:outline-none"
          >
            <option value="">All Indexability States</option>
            <option value="indexable">Indexable</option>
            <option value="noindex">Noindex</option>
            <option value="canonicalized">Canonicalized</option>
            <option value="blocked_by_robots">Blocked by robots.txt</option>
            <option value="error">HTTP Error</option>
          </select>
        </div>
      </div>

      {/* Crawled Pages Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-6">
            <LoadingSkeleton rows={6} />
          </div>
        ) : pages.length === 0 ? (
          <div className="py-16 text-center text-slate-500 text-xs">
            <p className="font-semibold text-slate-800 text-sm">No URLs matched your filters.</p>
            <p className="mt-1">Try resetting the search terms or indexability filter.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200 uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4 w-16">Status</th>
                  <th className="py-3 px-4">URL & Title</th>
                  <th className="py-3 px-3 w-28">Indexability</th>
                  <th className="py-3 px-3 w-20 text-center">Depth</th>
                  <th className="py-3 px-3 w-24">Words</th>
                  <th className="py-3 px-3 w-24">Links (In/Out)</th>
                  <th className="py-3 px-3 w-24">Latency</th>
                  <th className="py-3 px-4 w-20 text-center">Issues</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 font-sans">
                {pages.map((p) => {
                  const statusColor =
                    p.http_status >= 200 && p.http_status < 300
                      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                      : p.http_status >= 300 && p.http_status < 400
                      ? 'bg-blue-50 text-blue-700 border-blue-200'
                      : 'bg-rose-50 text-rose-700 border-rose-200';

                  return (
                    <tr key={p.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded text-[11px] font-mono font-bold border ${statusColor}`}>
                          {p.http_status || 'ERR'}
                        </span>
                      </td>

                      <td className="py-3 px-4 max-w-md">
                        <div className="font-mono text-slate-800 text-[11px] truncate flex items-center gap-1.5">
                          <a
                            href={p.final_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:underline hover:text-brand-700"
                          >
                            {p.final_url}
                          </a>
                          <ExternalLink className="w-3 h-3 text-slate-400 flex-shrink-0" />
                        </div>
                        <div className="text-slate-500 text-[11px] truncate mt-0.5 font-medium">
                          {p.title || <span className="text-rose-500 italic">No Title Tag</span>}
                        </div>
                      </td>

                      <td className="py-3 px-3">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[10px] font-medium capitalize ${
                            p.indexability_status === 'indexable'
                              ? 'bg-emerald-50 text-emerald-700'
                              : p.indexability_status === 'noindex'
                              ? 'bg-amber-50 text-amber-700'
                              : 'bg-slate-100 text-slate-600'
                          }`}
                        >
                          {p.indexability_status}
                        </span>
                      </td>

                      <td className="py-3 px-3 text-center font-mono text-slate-600">{p.crawl_depth}</td>

                      <td className="py-3 px-3 font-mono text-slate-600">{p.word_count.toLocaleString()}</td>

                      <td className="py-3 px-3 font-mono text-slate-600">
                        {p.internal_link_count} / {p.external_link_count}
                      </td>

                      <td className="py-3 px-3 font-mono text-slate-600">
                        {Math.round(p.response_time_ms)}ms
                      </td>

                      <td className="py-3 px-4 text-center">
                        <span
                          className={`font-mono font-bold px-2 py-0.5 rounded text-xs ${
                            (p.issue_count || 0) > 0
                              ? 'bg-rose-100 text-rose-800'
                              : 'bg-emerald-50 text-emerald-700'
                          }`}
                        >
                          {p.issue_count || 0}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        {totalPages > 1 && (
          <div className="px-6 py-3 border-t border-slate-200 flex items-center justify-between text-xs bg-slate-50/50">
            <span className="text-slate-500">
              Page {currentPage} of {totalPages}
            </span>
            <div className="flex gap-2">
              <button
                disabled={currentPage <= 1}
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                className="px-3 py-1.5 border border-slate-300 rounded bg-white text-slate-700 disabled:opacity-40"
              >
                <ChevronLeft className="w-3.5 h-3.5 inline mr-1" /> Previous
              </button>
              <button
                disabled={currentPage >= totalPages}
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                className="px-3 py-1.5 border border-slate-300 rounded bg-white text-slate-700 disabled:opacity-40"
              >
                Next <ChevronRight className="w-3.5 h-3.5 inline ml-1" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
