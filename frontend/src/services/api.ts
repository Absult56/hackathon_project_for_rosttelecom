import axios from 'axios'
import { companies as demoCompanies, projects as demoProjects, type Company, type InvestProject } from '../data'

const api = axios.create({ baseURL: '/api', timeout: 2500 })

export type DealEstimate = {
  min_price: number
  optimal_price: number
  recommended_margin_percent: number
  cost_structure: {
    equipment: number
    installation: number
    software_licenses: number
  }
  similar_deals_count: number
}

api.interceptors.request.use((config) => {
  const token = window.localStorage.getItem('rtk-demo-token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export async function login2FA(username: string, password: string, otpCode: string) {
  try {
    const response = await api.post('/auth/login-2fa', { username, password, otp_code: otpCode })
    return String(response.data.access_token)
  } catch (error) {
    if (axios.isAxiosError(error) && error.response && error.response.status !== 404 && error.response.status < 500) {
      throw new Error('invalid-credentials')
    }
    if (username === 'admin' && password === 'rtk_password' && otpCode === '123456') {
      return `demo.${Date.now()}`
    }
    throw new Error('service-unavailable')
  }
}

function asCompany(value: Record<string, unknown>): Company {
  return {
    id: Number(value.id),
    name: String(value.name ?? ''),
    inn: String(value.inn ?? ''),
    industry: String(value.industry ?? ''),
    revenue: Number(value.revenue ?? 0),
    growth: Number(value.revenue_growth ?? value.growth ?? 0),
    lat: Number(value.lat ?? 47.2225),
    lon: Number(value.lon ?? 39.7187),
    address: String(value.address ?? 'Ростовская область'),
    client: Boolean(value.is_rtk_client ?? value.client),
    zone: String(value.cluster_zone ?? value.zone ?? ''),
  }
}

const stageNames: Record<string, InvestProject['stage']> = {
  planning: 'Проектирование',
  construction: 'Строительство',
  launching: 'Запуск',
}

function asProject(value: Record<string, unknown>): InvestProject {
  const needs = value.target_needs ?? value.needs
  const stage = String(value.stage ?? '')
  return {
    id: Number(value.id),
    title: String(value.title ?? ''),
    investor: String(value.investor ?? ''),
    industry: String(value.industry ?? ''),
    stage: stageNames[stage] ?? (stage as InvestProject['stage']),
    budget: Number(value.budget ?? 0),
    date: String(value.event_date ?? value.date ?? ''),
    needs: Array.isArray(needs) ? needs.map(String) : [],
    lat: Number(value.lat ?? 47.2225),
    lon: Number(value.lon ?? 39.7187),
    description: String(value.description ?? ''),
  }
}

export async function loadCompanies(): Promise<{ data: Company[]; source: 'api' | 'demo' }> {
  try {
    const response = await api.get<Record<string, unknown>[]>('/radar/companies')
    return { data: response.data.map(asCompany), source: 'api' }
  } catch {
    return { data: demoCompanies, source: 'demo' }
  }
}

export async function loadProjects(): Promise<{ data: InvestProject[]; source: 'api' | 'demo' }> {
  try {
    const response = await api.get<Record<string, unknown>[]>('/invest/projects')
    return { data: response.data.map(asProject), source: 'api' }
  } catch {
    return { data: demoProjects, source: 'demo' }
  }
}

export async function calculateDeal(payload: Record<string, unknown>): Promise<DealEstimate | null> {
  try {
    const response = await api.post<DealEstimate>('/calculator/calculate', payload)
    return response.data
  } catch {
    return null
  }
}

export async function exportCompaniesCsv(params: Record<string, string | number | boolean>): Promise<Blob | null> {
  try {
    const response = await api.get<Blob>('/export/companies-csv', { params, responseType: 'blob', timeout: 900 })
    return response.data
  } catch {
    return null
  }
}

export async function generateProposalDoc(payload: Record<string, unknown>): Promise<Blob | null> {
  try {
    const response = await api.post<Blob>('/calculator/generate-doc', payload, { responseType: 'blob', timeout: 1200 })
    return response.data
  } catch {
    return null
  }
}