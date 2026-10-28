import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { DashboardPage } from '../pages/DashboardPage';
import { api } from '../services/api';

vi.mock('../services/api', () => ({
  api: {
    getDashboardStats: vi.fn(),
    getSampleReport: vi.fn(),
  },
}));

// Mock ResizeObserver for Recharts
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

describe('DashboardPage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially', () => {
    (api.getDashboardStats as any).mockReturnValue(new Promise(() => {}));
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );
    expect(document.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('renders dashboard metrics, charts, and recent audits table', async () => {
    (api.getDashboardStats as any).mockResolvedValue({
      total_audits: 5,
      websites_audited: 3,
      total_issues: 24,
      critical_issues: 4,
      high_issues: 6,
      critical_and_high_issues: 10,
      avg_health_score: 82.5,
      recent_audits: [
        {
          id: 'test-audit-1',
          normalized_domain: 'scalezix.com',
          submitted_url: 'https://scalezix.com',
          status: 'completed',
          seo_health_score: 82.5,
          total_crawled_pages: 18,
          total_discovered_pages: 18,
          created_at: new Date().toISOString(),
        },
      ],
      severity_distribution: { critical: 4, high: 6, medium: 8, low: 4, informational: 2 },
      category_distribution: { on_page: 8, crawlability: 6, internal_linking: 4 },
    });

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Technical SEO Dashboard/i)).toBeInTheDocument();
    });

    // Verify Metric Cards
    expect(screen.getByText('3')).toBeInTheDocument(); // websites audited
    expect(screen.getByText('82.5/100')).toBeInTheDocument(); // avg health score
    expect(screen.getByText('10')).toBeInTheDocument(); // critical & high deficiencies
    expect(screen.getByText('24')).toBeInTheDocument(); // total issues

    // Verify Recent Audits Table
    expect(screen.getByText('scalezix.com')).toBeInTheDocument();
    expect(screen.getByText(/View Results/i)).toBeInTheDocument();

    // Verify Action buttons
    expect(screen.getByRole('link', { name: /start new audit/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /scalezix sample report/i })).toBeInTheDocument();
  });
});
