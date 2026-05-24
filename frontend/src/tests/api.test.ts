import { describe, it, expect, vi, beforeEach } from 'vitest'

beforeEach(() => {
  vi.restoreAllMocks()
  sessionStorage.clear()
})

describe('api', () => {
  it('setAdminToken stores and retrieves token', async () => {
    const { api } = await import('../api')
    api.setAdminToken('my-token')
    expect(api.getAdminToken()).toBe('my-token')
  })

  it('setAdminToken with empty string clears token', async () => {
    const { api } = await import('../api')
    api.setAdminToken('my-token')
    api.setAdminToken('')
    expect(api.getAdminToken()).toBe('')
  })

  it('getAdminToken returns empty string when no token set', async () => {
    const { api } = await import('../api')
    expect(api.getAdminToken()).toBe('')
  })
})

describe('store', () => {
  it('auth store starts unauthenticated', async () => {
    const { useAuthStore } = await import('../store')
    const state = useAuthStore.getState()
    expect(state.isAuthenticated()).toBe(false)
    expect(state.token).toBeNull()
    expect(state.user).toBeNull()
  })

  it('setAuth stores token and user', async () => {
    const { useAuthStore } = await import('../store')
    useAuthStore.getState().setAuth('token-123', {
      id: '1',
      email: 'a@b.com',
      name: 'Test',
      role: 'admin',
    })
    const state = useAuthStore.getState()
    expect(state.token).toBe('token-123')
    expect(state.user?.email).toBe('a@b.com')
    expect(state.isAuthenticated()).toBe(true)
  })

  it('clearAuth removes token and user', async () => {
    const { useAuthStore } = await import('../store')
    useAuthStore.getState().setAuth('token-123', {
      id: '1',
      email: 'a@b.com',
      name: 'Test',
      role: 'admin',
    })
    useAuthStore.getState().clearAuth()
    const state = useAuthStore.getState()
    expect(state.token).toBeNull()
    expect(state.user).toBeNull()
    expect(state.isAuthenticated()).toBe(false)
  })

  it('toggleSidebar toggles sidebarOpen', async () => {
    const { useUiStore } = await import('../store')
    expect(useUiStore.getState().sidebarOpen).toBe(false)
    useUiStore.getState().toggleSidebar()
    expect(useUiStore.getState().sidebarOpen).toBe(true)
    useUiStore.getState().toggleSidebar()
    expect(useUiStore.getState().sidebarOpen).toBe(false)
  })
})
