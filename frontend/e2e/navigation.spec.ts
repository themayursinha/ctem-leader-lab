import { test, expect } from '@playwright/test'

test.describe('CTEM Leader Lab — Navigation', () => {
  test('Dashboard loads with program overview', async ({ page }) => {
    await page.goto('/#/')
    await expect(page.locator('.page-title')).toContainText('Northstar')
    await expect(page.locator('.metric-grid .metric-card')).toHaveCount(4)
    await expect(page.locator('.cycle-list .cycle-item')).toHaveCount(5)
  })

  test('All 9 pages load without errors', async ({ page }) => {
    const views: { path: string; heading: string }[] = [
      { path: '/#/', heading: 'Northstar' },
      { path: '/#/scoping', heading: 'Scoping' },
      { path: '/#/discovery', heading: 'Discovery' },
      { path: '/#/prioritization', heading: 'Prioritization' },
      { path: '/#/validation', heading: 'Validation' },
      { path: '/#/mobilization', heading: 'Mobilization' },
      { path: '/#/workshop-pack', heading: 'Workshop Pack' },
      { path: '/#/guide', heading: 'User Guide' },
    ]

    for (const { path, heading } of views) {
      await page.goto(path)
      await page.waitForLoadState('networkidle')
      await expect(page.locator('.page-title')).toContainText(heading)
      await expect(page.locator('.notice-panel.error')).toHaveCount(0)
      await expect(page.locator('.error-boundary')).toHaveCount(0)
    }
  })
})
