import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { NewAuditPage } from '../pages/NewAuditPage';
import { api } from '../services/api';

vi.mock('../services/api', () => ({
  api: {
    createAudit: vi.fn(),
  },
}));

describe('NewAuditPage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all form input fields and labels', () => {
    render(
      <BrowserRouter>
        <NewAuditPage />
      </BrowserRouter>
    );

    expect(screen.getByText(/Configure New Technical SEO Audit/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/https:\/\/example.com/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/e\.g\., Scalezix Production Technical Audit/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /launch technical audit/i })).toBeInTheDocument();
    expect(screen.getByText(/I verify that I have permission to crawl this target domain/i)).toBeInTheDocument();
  });

  it('shows error if submitted without authorization consent checkbox', async () => {
    render(
      <BrowserRouter>
        <NewAuditPage />
      </BrowserRouter>
    );

    const urlInput = screen.getByPlaceholderText(/https:\/\/example.com/i);
    fireEvent.change(urlInput, { target: { value: 'https://testsite.com' } });

    const submitBtn = screen.getByRole('button', { name: /launch technical audit/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/Please acknowledge crawl authorization and robots.txt compliance/i)).toBeInTheDocument();
    });
    expect(api.createAudit).not.toHaveBeenCalled();
  });

  it('submits successfully when URL and consent checkbox are provided', async () => {
    (api.createAudit as any).mockResolvedValue({ id: 'new-audit-id-123' });

    render(
      <BrowserRouter>
        <NewAuditPage />
      </BrowserRouter>
    );

    const urlInput = screen.getByPlaceholderText(/https:\/\/example.com/i);
    fireEvent.change(urlInput, { target: { value: 'https://scalezix.com' } });

    const consentCheckbox = screen.getByRole('checkbox');
    fireEvent.click(consentCheckbox);

    const submitBtn = screen.getByRole('button', { name: /launch technical audit/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(api.createAudit).toHaveBeenCalledWith(
        expect.objectContaining({
          url: 'https://scalezix.com',
          max_pages: 25,
          max_depth: 3,
        })
      );
    });
  });
});
