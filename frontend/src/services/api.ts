import axios from 'axios'
import { companies as demoCompanies, projects as demoProjects, type Company, type InvestProject } from '../data'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 5000,
})

function expireUnauthorizedSession(error: unknown) {
  if (axios.isAxiosError(error) && error.response?.status === 401) {
    window.localStorage.removeItem('rtk-demo-token')
    window.dispatchEvent(new Event('api-auth-expired'))
  }
}

export type Benchmark = { title: string; price: number; margin: number }
export type DealEstimate = {
  cost_price: number
  min_price: number
  optimal_price: number
  margin_rub: number
  margin_percent: number
  benchmarks: Benchmark[]
}

api.interceptors.request.use((config) => {
  const token = window.localStorage.getItem('rtk-demo-token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export async function request2FACode(email: string): Promise<{ demo: boolean; hint: string }> {
  try {
    const response = await api.post('/auth/request-code', { email })
    return { demo: false, hint: String(response.data.demo_hint ?? response.data.message ?? '') }
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) throw new Error('request-failed')
    return { demo: true, hint: 'Backend недоступен: для автономного демо используйте мастер-код 123456.' }
  }
}

export async function verify2FA(email: string, code: string, offlineDemo: boolean): Promise<string> {
  try {
    const response = await api.post('/auth/verify-2fa', { email, code })
    return String(response.data.access_token)
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) throw new Error('invalid-code')
    if (offlineDemo && code === '123456') return `demo.${Date.now()}`
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
    revenueEstimated: Boolean(value.revenue_estimated ?? true),
    growth: Number(value.revenue_growth ?? value.growth ?? 0),
    lat: Number(value.lat ?? 47.2225),
    lon: Number(value.lon ?? 39.7187),
    address: String(value.address ?? 'Ростовская область'),
    client: Boolean(value.is_rtk_client ?? value.client),
    whiteSpot: Boolean(value.is_white_spot ?? value.white_spot),
    zone: String(value.cluster_zone ?? value.zone ?? ''),
  }
}

const stageNames: Record<string, InvestProject['stage']> = {
  planning: 'Проектирование',
  construction: 'Строительство',
  launching: 'Запуск',
  'проектирование': 'Проектирование',
  'стройка': 'Строительство',
  'ввод': 'Запуск',
  'ввод в эксплуатацию': 'Запуск',
}

const needNames: Record<string, string> = {
  fiber_optics: 'Оптическая сеть',
  cctv: 'Видеонаблюдение',
  data_center: 'ЦОД',
  telephony: 'IP-телефония',
  access_control: 'СКУД',
  it_infra: 'IT-инфраструктура',
  asutp: 'АСУ ТП',
}

function asProject(value: Record<string, unknown>): InvestProject {
  const rawNeeds = value.target_needs ?? value.needs
  const needs = Array.isArray(rawNeeds)
    ? rawNeeds.map(String)
    : typeof rawNeeds === 'string'
      ? rawNeeds.split(',').map((need) => need.trim()).filter(Boolean)
      : []
  const stage = String(value.stage ?? '').toLocaleLowerCase('ru-RU')
  return {
    id: Number(value.id),
    title: String(value.title ?? ''),
    investor: String(value.investor ?? ''),
    industry: String(value.industry ?? ''),
    stage: stageNames[stage] ?? (stage as InvestProject['stage']),
    budget: Number(value.budget ?? 0),
    date: String(value.event_date ?? value.date ?? ''),
    needs: needs.map((need) => needNames[need] ?? need),
    lat: Number(value.lat ?? 47.2225),
    lon: Number(value.lon ?? 39.7187),
    description: String(value.description ?? ''),
  }
}

export async function loadCompanies(): Promise<{ data: Company[]; source: 'api' | 'demo' }> {
  try {
    const response = await api.get<Record<string, unknown>[]>('/radar/companies')
    return { data: response.data.map(asCompany), source: 'api' }
  } catch (error) {
    expireUnauthorizedSession(error)
    return { data: demoCompanies, source: 'demo' }
  }
}

export async function loadProjects(): Promise<{ data: InvestProject[]; source: 'api' | 'demo' }> {
  try {
    const response = await api.get<Record<string, unknown>[]>('/invest/projects')
    return { data: response.data.map(asProject), source: 'api' }
  } catch (error) {
    expireUnauthorizedSession(error)
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
    const response = await api.get<Blob>('/export/companies/csv', { params, responseType: 'blob', timeout: 1800 })
    return response.data
  } catch {
    return null
  }
}

export async function generateProposalDoc(payload: Record<string, unknown>): Promise<Blob | null> {
  try {
    const response = await api.post<Blob>('/calculator/export-docx', payload, { responseType: 'blob', timeout: 1800 })
    return response.data
  } catch {
    return null
  }
}