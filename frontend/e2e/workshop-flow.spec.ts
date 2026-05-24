import { test, expect } from '@playwright/test'

async function dismissOverlays(page: import('@playwright/test').Page) {
  try {
    const cta = page.locator('.modal-cta')
    if (await cta.isVisible({ timeout: 1500 })) await cta.click()
  } catch {}
  try {
    const banner = page.locator('.demo-banner-close')
    if (await banner.isVisible({ timeout: 1000 })) await banner.click()
  } catch {}
}

async function navigateTo(page: import('@playwright/test').Page, path: string) {
  await page.goto(path)
  await dismissOverlays(page)
}

test.describe('CTEM Leader Lab — Workshop Flow', () => {
  test('Dashboard shows program maturity chart', async ({ page }) => {
    await navigateTo(page, '/#/')
    await expect(page.locator('.maturity-chart')).toBeVisible()
    await expect(page.locator('.maturity-row')).toHaveCount(5)
    await expect(page.locator('.principle-card').first()).toBeVisible()
  })

  test('Scoping shows business services and crown jewel worksheet', async ({ page }) => {
    await navigateTo(page, '/#/scoping')
    await expect(page.locator('.page-title')).toContainText('Scoping')
    await expect(page.locator('.service-card')).toHaveCount(4)
    await expect(page.locator('.prompt-card').first()).toBeVisible()
  })

  test('Scoping shows asset inventory with table data', async ({ page }) => {
    await navigateTo(page, '/#/scoping')
    const rows = page.locator('.data-table tbody tr')
    await expect(rows.first()).toContainText('Payment Gateway API')
  })

  test('Discovery shows exposure inventory', async ({ page }) => {
    await navigateTo(page, '/#/discovery')
    await expect(page.locator('.page-title')).toContainText('Discovery')
    await expect(page.locator('.data-table tbody tr').first()).toBeVisible()
  })

  test('Prioritization shows ranked risks with CTEM scores', async ({ page }) => {
    await navigateTo(page, '/#/prioritization')
    await expect(page.locator('.page-title')).toContainText('Prioritization')
    await expect(page.locator('.comparison-strip')).toBeVisible()
    const riskCards = page.locator('.risk-card')
    await expect(riskCards.first().locator('.risk-score strong')).toBeVisible()
  })

  test('Prioritization shows score drivers', async ({ page }) => {
    await navigateTo(page, '/#/prioritization')
    const drivers = page.locator('.driver-grid .driver')
    await expect(drivers.first()).toBeVisible()
  })

  test('Validation shows attack paths with steps', async ({ page }) => {
    await navigateTo(page, '/#/validation')
    await expect(page.locator('.page-title')).toContainText('Validation')
    await expect(page.locator('.path-card')).toHaveCount(2)
    await expect(page.locator('.path-step').first()).toBeVisible()
  })

  test('Mobilization shows kanban board', async ({ page }) => {
    await navigateTo(page, '/#/mobilization')
    await expect(page.locator('.page-title')).toContainText('Mobilization')
    await expect(page.locator('.board-column')).toHaveCount(4)
    await expect(page.locator('.action-card').first()).toBeVisible()
  })

  test('Mobilization shows RACI and roadmap', async ({ page }) => {
    await navigateTo(page, '/#/mobilization')
    await expect(page.locator('text=RACI')).toBeVisible()
    await expect(page.locator('text=30/60/90 Roadmap')).toBeVisible()
    await expect(page.locator('.roadmap-item')).toHaveCount(3)
  })

  test('Workshop Pack shows action buttons', async ({ page }) => {
    await navigateTo(page, '/#/workshop-pack')
    await expect(page.locator('.page-title')).toContainText('Workshop Pack')
    await expect(page.locator('button:has-text("Copy Markdown")')).toBeVisible()
    await expect(page.locator('button:has-text("Download JSON")')).toBeVisible()
    await expect(page.locator('button:has-text("Print")')).toBeVisible()
  })

  test('Workshop Pack shows all 4 template parts', async ({ page }) => {
    await navigateTo(page, '/#/workshop-pack')
    await expect(page.locator('text=Crown-Jewel Scoping Worksheet')).toBeVisible()
    await expect(page.locator('text=Prioritization Rubric')).toBeVisible()
    await expect(page.locator('text=Validation Evidence Checklist')).toBeVisible()
    await expect(page.locator('text=Mobilization Template')).toBeVisible()
  })

  test('User Guide tabs work', async ({ page }) => {
    await navigateTo(page, '/#/guide')
    await expect(page.locator('.page-title')).toContainText('User Guide')
    const tocItems = page.locator('.guide-toc-item')
    await expect(tocItems).toHaveCount(4)
    await tocItems.last().click({ force: true })
    await expect(page.locator('text=CTEM Score')).toBeVisible()
    await expect(page.locator('text=EPSS')).toBeVisible()
  })

  test('No error boundaries on any page', async ({ page }) => {
    const views = ['/#/', '/#/scoping', '/#/discovery', '/#/prioritization',
      '/#/validation', '/#/mobilization', '/#/workshop-pack', '/#/guide']
    for (const path of views) {
      await navigateTo(page, path)
      await page.waitForLoadState('networkidle')
      await expect(page.locator('.error-boundary')).toHaveCount(0)
    }
  })
})
