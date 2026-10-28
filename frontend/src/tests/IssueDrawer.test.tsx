import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { IssueDrawer } from '../components/IssueDrawer';
import { SEOIssue } from '../types/api';

const mockIssue: SEOIssue = {
  id: 'issue-123',
  audit_id: 'audit-001',
  issue_code: 'ERR_TITLE_MISSING',
  title: 'Missing Page Title Tag',
  category: 'on_page',
  severity: 'critical',
  priority_score: 91.5,
  impact: 0.95,
  confidence: 1.0,
  estimated_effort: 0.1,
  description: 'The page lacks a title tag in its HTML head.',
  why_it_matters: 'The title tag is the primary anchor used by search engines.',
  suggested_fix: 'Add a concise, descriptive title tag.',
  example_fix: '<title>Primary Keyword | Brand</title>',
  status: 'open',
  affected_page_count: 1,
  created_at: new Date().toISOString(),
  evidences: [
    {
      id: 'ev-1',
      issue_id: 'issue-123',
      page_url: 'https://example.com/missing-title',
      observed_value: 'No title found',
      expected_value: 'Descriptive title tag',
      evidence_snippet: '<head></head>',
      evidence_type: 'html_element',
      explanation: 'Title element omitted.',
    },
  ],
};

describe('IssueDrawer Component', () => {
  it('renders issue details, evidence, and code snippet', () => {
    const handleClose = vi.fn();
    const handleStatusChange = vi.fn();

    render(
      <IssueDrawer
        issue={mockIssue}
        onClose={handleClose}
        onStatusChange={handleStatusChange}
      />
    );

    expect(screen.getByText('Missing Page Title Tag')).toBeInTheDocument();
    expect(screen.getByText('ERR_TITLE_MISSING')).toBeInTheDocument();
    expect(screen.getByText('92')).toBeInTheDocument(); // Math.round(91.5)
    expect(screen.getByText('The page lacks a title tag in its HTML head.')).toBeInTheDocument();
    expect(screen.getByText('The title tag is the primary anchor used by search engines.')).toBeInTheDocument();
    expect(screen.getByText('<title>Primary Keyword | Brand</title>')).toBeInTheDocument();
    expect(screen.getByText('https://example.com/missing-title')).toBeInTheDocument();
  });

  it('triggers onStatusChange when status dropdown is changed', async () => {
    const handleClose = vi.fn();
    const handleStatusChange = vi.fn().mockResolvedValue(undefined);

    render(
      <IssueDrawer
        issue={mockIssue}
        onClose={handleClose}
        onStatusChange={handleStatusChange}
      />
    );

    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'resolved' } });

    await waitFor(() => {
      expect(handleStatusChange).toHaveBeenCalledWith('issue-123', 'resolved');
    });
  });

  it('calls onClose when close buttons are clicked', () => {
    const handleClose = vi.fn();
    const handleStatusChange = vi.fn();

    render(
      <IssueDrawer
        issue={mockIssue}
        onClose={handleClose}
        onStatusChange={handleStatusChange}
      />
    );

    const closeBtn = screen.getByRole('button', { name: /close details/i });
    fireEvent.click(closeBtn);
    expect(handleClose).toHaveBeenCalled();
  });
});
