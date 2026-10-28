import { test, expect } from '@playwright/test';

test.describe('SEO Audit Pro — Comprehensive Feature & Button Verification', () => {
  test('1. Landing Page, Navigation & Scalezix Sample Report', async ({ page }) => {
    // Navigate to landing page
    await page.goto('/');

    // Verify Title & Hero
    await expect(page).toHaveTitle(/SEO Audit Pro/i);
    await expect(page.getByText('Find SEO Issues. Prioritize Fixes. Improve Your Website.')).toBeVisible();

    // Verify presence of core buttons
    const startAuditBtn = page.getByRole('button', { name: /start audit/i });
    await expect(startAuditBtn).toBeVisible();

    const sampleBtn = page.getByRole('button', { name: /inspect scalezix sample report/i });
    await expect(sampleBtn).toBeVisible();

    // Click Scalezix Sample Report button
    await sampleBtn.click();

    // Should navigate to audit results
    await expect(page).toHaveURL(/.*audits\/scalezix-sample-audit-001/);
    await expect(page.getByRole('heading', { name: 'scalezix.com' })).toBeVisible();
    await expect(page.getByText('SEO Health Score')).toBeVisible();

    // Verify score badge is visible
    await expect(page.getByText('78.5')).toBeVisible();

    // Take screenshot of sample audit results
    await page.screenshot({ path: 'e2e-screenshots/01-audit-results.png' });
  });

  test('2. Audit Results Table, Filters, and Issue Drawer Details', async ({ page }) => {
    await page.goto('/audits/scalezix-sample-audit-001');

    // Verify Roadmap Table
    await expect(page.getByText(/Prioritized Fix Roadmap/i)).toBeVisible();
    await expect(page.getByText(/Broken Internal Page Returning HTTP 404/i).first()).toBeVisible();

    // Test Search Filter
    const searchInput = page.getByPlaceholder(/search issues by keyword/i);
    await searchInput.fill('404');
    await expect(page.getByText('Broken Internal Page Returning HTTP 404').first()).toBeVisible();

    // Clear search
    await page.getByRole('button', { name: /clear filters/i }).click();

    // Click on the first issue row to open the Slide-over Drawer
    await page.getByText('Broken Internal Page Returning HTTP 404').first().click();

    // Verify Issue Drawer contents
    await expect(page.getByText('Issue Summary')).toBeVisible();
    await expect(page.getByText('Why This Matters for SEO')).toBeVisible();
    await expect(page.getByText('Recommended Correction')).toBeVisible();
    await expect(page.getByText(/Stored Audit Evidence/i)).toBeVisible();

    // Test Status Select in drawer
    const statusSelect = page.locator('select').filter({ hasText: /open|in progress|resolved|ignored/i }).first();
    await expect(statusSelect).toBeVisible();
    await statusSelect.selectOption('in_progress');

    // Close Details Drawer
    await page.getByRole('button', { name: /close details/i }).click();
    await expect(page.getByText('Issue Summary')).not.toBeVisible();
  });

  test('3. Crawled Pages URL Table & Pagination', async ({ page }) => {
    await page.goto('/audits/scalezix-sample-audit-001/pages');

    // Verify header and table
    await expect(page.getByText(/Discovered & Crawled URLs/i)).toBeVisible();
    await expect(page.getByText('https://scalezix.com/').first()).toBeVisible();
    await expect(page.getByText('https://scalezix.com/services').first()).toBeVisible();
    await expect(page.getByText('https://scalezix.com/case-studies').first()).toBeVisible();

    // Filter by indexability status
    const filterSelect = page.locator('select').first();
    await filterSelect.selectOption('indexable');
    await expect(page.getByText('https://scalezix.com/').first()).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: 'e2e-screenshots/02-crawled-pages.png' });
  });

  test('4. Dashboard Metrics & Visualization Charts', async ({ page }) => {
    await page.goto('/dashboard');

    // Verify dashboard metrics
    await expect(page.getByText('Technical SEO Dashboard')).toBeVisible();
    await expect(page.getByText('Websites Audited')).toBeVisible();
    await expect(page.getByText('Average Health Score')).toBeVisible();
    await expect(page.getByText('Critical & High Deficiencies')).toBeVisible();
    await expect(page.getByText('Total Issues Identified')).toBeVisible();

    // Verify recent audits table
    await expect(page.getByText('Recent Website Audits')).toBeVisible();
    await expect(page.getByText('scalezix.com', { exact: true }).first()).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: 'e2e-screenshots/03-dashboard.png' });
  });

  test('5. New Audit Form Validation & Launch', async ({ page }) => {
    await page.goto('/audits/new');

    await expect(page.getByText('Configure New Technical SEO Audit')).toBeVisible();

    // Submit without input should trigger HTML5 or form validation
    const submitBtn = page.getByRole('button', { name: /launch technical audit/i });
    await expect(submitBtn).toBeVisible();

    // Enter target URL
    const urlInput = page.getByPlaceholder('https://example.com');
    await urlInput.fill('http://127.0.0.1:8765');

    // Check authorization consent
    const consentCheckbox = page.getByRole('checkbox');
    await consentCheckbox.check();

    // Launch audit
    await submitBtn.click();

    // Should navigate to progress page
    await expect(page).toHaveURL(/.*audits\/.*\/progress/);
    await expect(page.getByText(/Auditing Website in Progress|Audit Completed Successfully/i)).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: 'e2e-screenshots/04-progress-page.png' });
  });

  test('6. Reports Page & Comparison Engine', async ({ page }) => {
    await page.goto('/reports');

    await expect(page.getByText('Audit Reports & Historical Records')).toBeVisible();
    await expect(page.getByText('Audit Comparison Engine')).toBeVisible();
    await expect(page.getByText('Historical Audit Records')).toBeVisible();

    // Verify export buttons
    await expect(page.locator('a[download]').filter({ hasText: 'PDF' }).first()).toBeVisible();
    await expect(page.locator('a[download]').filter({ hasText: 'CSV' }).first()).toBeVisible();
    await expect(page.locator('a[download]').filter({ hasText: 'JSON' }).first()).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: 'e2e-screenshots/05-reports.png' });
  });

  test('7. Settings & Documentation Page', async ({ page }) => {
    await page.goto('/settings');

    await expect(page.getByText('System Settings & Documentation')).toBeVisible();
    await expect(page.getByText(/Backend API & Database Connectivity/i)).toBeVisible();
    await expect(page.getByText(/Deterministic Fix Prioritization Formula/i)).toBeVisible();
    await expect(page.getByText(/SEO Health Score Calculation/i)).toBeVisible();
    await expect(page.getByText(/Server-Side Request Forgery \(SSRF\) Firewall/i)).toBeVisible();

    // Take screenshot
    await page.screenshot({ path: 'e2e-screenshots/06-settings.png' });
  });
});
