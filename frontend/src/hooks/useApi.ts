import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api'
import type {
  ProgramSummary,
  MaturityDomain,
  BusinessService,
  Asset,
  Exposure,
  PrioritizedExposure,
  AttackPath,
  RemediationAction,
  WorkshopArtifacts,
  ImportResult,
} from '../types/api'

export function useProgramSummary() {
  return useQuery<ProgramSummary>({
    queryKey: ['program-summary'],
    queryFn: api.getProgramSummary,
    staleTime: 30_000,
  })
}

export function useMaturity() {
  return useQuery<MaturityDomain[]>({
    queryKey: ['maturity'],
    queryFn: api.getMaturity,
    staleTime: 30_000,
  })
}

export function useBusinessServices() {
  return useQuery<BusinessService[]>({
    queryKey: ['business-services'],
    queryFn: api.getBusinessServices,
    staleTime: 30_000,
  })
}

export function useAssets() {
  return useQuery<Asset[]>({
    queryKey: ['assets'],
    queryFn: api.getAssets,
    staleTime: 30_000,
  })
}

export function useExposures() {
  return useQuery<Exposure[]>({
    queryKey: ['exposures'],
    queryFn: api.getExposures,
    staleTime: 30_000,
  })
}

export function usePrioritizedExposures() {
  return useQuery<PrioritizedExposure[]>({
    queryKey: ['prioritized-exposures'],
    queryFn: api.getPrioritizedExposures,
    staleTime: 30_000,
  })
}

export function useAttackPaths() {
  return useQuery<AttackPath[]>({
    queryKey: ['attack-paths'],
    queryFn: api.getAttackPaths,
    staleTime: 30_000,
  })
}

export function useRemediationActions() {
  return useQuery<RemediationAction[]>({
    queryKey: ['remediation-actions'],
    queryFn: api.getRemediationActions,
    staleTime: 30_000,
  })
}

export function useWorkshopArtifacts() {
  return useQuery<WorkshopArtifacts>({
    queryKey: ['workshop-artifacts'],
    queryFn: api.getWorkshopArtifacts,
    staleTime: 30_000,
  })
}

export function useSessions() {
  return useQuery({
    queryKey: ['sessions'],
    queryFn: api.listSessions,
    staleTime: 10_000,
  })
}

export function useAuditEvents(limit = 100) {
  return useQuery({
    queryKey: ['audit-events', limit],
    queryFn: () => api.listAuditEvents(limit),
    staleTime: 10_000,
  })
}

export function useSaveSession() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (name: string) => api.saveSession(name),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['sessions'] }),
  })
}

export function useLoadSession() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (sessionId: string) => api.loadSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries()
    },
  })
}

export function useDeleteSession() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (sessionId: string) => api.deleteSession(sessionId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['sessions'] }),
  })
}

export function useResetData() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.resetData,
    onSuccess: () => queryClient.invalidateQueries(),
  })
}

export function useImportAssets() {
  const queryClient = useQueryClient()
  return useMutation<ImportResult, Error, File>({
    mutationFn: (file: File) => api.importAssetsCsv(file),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['assets'] }),
  })
}

export function useImportExposures() {
  const queryClient = useQueryClient()
  return useMutation<ImportResult, Error, File>({
    mutationFn: (file: File) => api.importExposuresCsv(file),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['exposures'] }),
  })
}

export function useImportRemediation() {
  const queryClient = useQueryClient()
  return useMutation<ImportResult, Error, File>({
    mutationFn: (file: File) => api.importRemediationCsv(file),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['remediation-actions'] }),
  })
}
