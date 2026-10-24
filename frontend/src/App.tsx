import { useEffect, useMemo, useState, type FormEvent, type ReactNode } from 'react'
import * as L from 'leaflet'
import { Document, HeadingLevel, Packer, Paragraph, TextRun } from 'docx'
import {
  ArrowDownToLine, ArrowRight, BadgeCheck, Building2, Calculator, CalendarDays,
  Check, ChevronDown, CircleHelp, FileText, Filter, Layers3, LogOut, MapPin,
  Search, ShieldCheck, SlidersHorizontal, TrendingDown, TrendingUp, Wallet,
} from 'lucide-react'
import {
  Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from 'recharts'
import MarkerClusterGroup from 'react-leaflet-cluster'
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import 'react-leaflet-cluster/lib/assets/MarkerCluster.css'
import 'react-leaflet-cluster/lib/assets/MarkerCluster.Default.css'
import 'leaflet.heat'
import { companies as demoCompanies, formatMoney, industries, projects as demoProjects, type Company, type InvestProject } from './data'
import { calculateDeal, exportCompaniesCsv, generateProposalDoc, loadCompanies, loadProjects, request2FACode, verify2FA, type DealEstimate } from './services/api'

type Module = 'radar' | 'invest' | 'calculator'
type MapPoint = { id: number; name: string; lat: number; lon: number; color: string; detail: string; weight?: number; whiteSpot?: boolean }

const initialToken = () => window.localStorage.getItem('rtk-demo-token')
const isInRostovRegion = (lat: number, lon: number) => lat >= 45.8 && lat <= 49.0 && lon >= 38.2 && lon <= 45.2

function MapViewport({ center }: { center: [number, number] }) {
  const map = useMap()
  useEffect(() => {
    const next = L.latLng(center[0], center[1])
    if (map.getCenter().distanceTo(next) > 100) map.flyTo(next, map.getZoom(), { duration: 0.55 })
  }, [center[0], center[1], map])
  return null
}

function MapZoomWatcher({ onZoomChange }: { onZoomChange: (zoom: number) => void }) {
  const map = useMap()
  useEffect(() => {
    const updateZoom = () => onZoomChange(map.getZoom())
    updateZoom()
    map.on('zoomend', updateZoom)
    return () => { map.off('zoomend', updateZoom) }
  }, [map, onZoomChange])
  return null
}

function HeatLayer({ points, enabled }: { points: MapPoint[]; enabled: boolean }) {
  const map = useMap()
  useEffect(() => {
    if (!enabled || !points.length) return
    const layer = L.heatLayer(points.map((point) => [point.lat, point.lon, Math.max(0.15, Math.min(1, (point.weight ?? 100) / 1000))]), {
      radius: 30,
      blur: 24,
      maxZoom: 15,
      gradient: { 0.25: '#38a68c', 0.55: '#ffbd55', 0.82: '#ff653f', 1: '#7028d8' },
    }).addTo(map)
    return () => { map.removeLayer(layer) }
  }, [enabled, map, points])
  return null
}

function GeoMap({ points, selectedId, center, onSelect, heatmap = false, clusterAtZoom = 13 }: {
  points: MapPoint[]; selectedId: number; center: [number, number]; onSelect: (id: number) => void; heatmap?: boolean; clusterAtZoom?: number
}) {
  const [zoom, setZoom] = useState(12)
  return (
    <>
      <MapContainer center={center} zoom={12} scrollWheelZoom className="leaflet-map">
        <MapViewport center={center} />
        <MapZoomWatcher onZoomChange={setZoom} />
        <HeatLayer points={points} enabled={heatmap && zoom < clusterAtZoom} />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {zoom >= clusterAtZoom && <MarkerClusterGroup
          chunkedLoading
          showCoverageOnHover={false}
          maxClusterRadius={42}
          iconCreateFunction={(cluster: { getChildCount: () => number }) => L.divIcon({
            html: `<span>${cluster.getChildCount()}</span>`,
            className: 'company-cluster',
            iconSize: L.point(34, 34),
          })}
        >
          {points.map((point) => (
            <Marker
              key={point.id}
              position={[point.lat, point.lon]}
              icon={L.divIcon({
                html: `<span class="company-marker${point.id === selectedId ? ' selected' : ''}${point.whiteSpot ? ' white-spot' : ''}" style="--marker-color:${point.color}"></span>`,
                className: 'company-marker-icon',
                iconSize: [24, 24],
                iconAnchor: [12, 12],
              })}
              eventHandlers={{ click: () => onSelect(point.id) }}
            >
              <Popup><strong>{point.name}</strong><br />{point.detail}</Popup>
            </Marker>
          ))}
        </MarkerClusterGroup>}
      </MapContainer>
      <span className="map-mode-label">{zoom < clusterAtZoom ? heatmap ? 'Плотность рынка' : 'Тепловой слой выключен' : 'Компании · кластеры'}</span>
    </>
  )
}

const modules: { id: Module; label: string; icon: typeof MapPin }[] = [
  { id: 'radar', label: 'Радар присутствия', icon: MapPin },
  { id: 'invest', label: 'Инвест-навигатор', icon: Layers3 },
  { id: 'calculator', label: 'Калькулятор сделок', icon: Calculator },
]

function Brand() {
  return <div className="brand-lockup"><span className="brand-mark"><span /></span><span className="brand-name">Ростелеком<small>коммерческая аналитика</small></span></div>
}

function Login({ onLogin }: { onLogin: (token: string) => void }) {
  const [email, setEmail] = useState('manager@rt.ru')
  const [otp, setOtp] = useState('123456')
  const [error, setError] = useState('')
  const [hint, setHint] = useState('')
  const [codeRequested, setCodeRequested] = useState(false)
  const [offlineDemo, setOfflineDemo] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      if (!codeRequested) {
        const result = await request2FACode(email)
        setOfflineDemo(result.demo)
        setHint(result.hint)
        setCodeRequested(true)
        return
      }
      const token = await verify2FA(email, otp, offlineDemo)
      window.localStorage.setItem('rtk-demo-token', token)
      onLogin(token)
    } catch (cause) {
      setError(cause instanceof Error && cause.message === 'invalid-code'
        ? 'Код не подошёл. Проверьте его и попробуйте ещё раз.'
        : 'Не удалось запросить или подтвердить код. Проверьте email и доступность backend.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <Brand />
        <div className="auth-copy">
          <span className="eyebrow"><span className="live-dot" /> ЕДИНЫЙ КОММЕРЧЕСКИЙ КОНТУР</span>
          <h1>Видеть рынок.<br /><span>Действовать точнее.</span></h1>
          <p>Геоаналитика, инвестиционные события и оценка проектов в одном рабочем пространстве.</p>
        </div>
        <form className="login-form" onSubmit={submit}>
          <div className="form-heading"><div><span className="eyebrow">ЗАЩИЩЁННЫЙ ДОСТУП</span><h2>Войти в систему</h2></div><ShieldCheck size={22} /></div>
          <label>Email<input type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} /></label>
          {codeRequested && <label>Код подтверждения <span className="label-aside">SMS · Telegram · мастер-код</span><input inputMode="numeric" autoComplete="one-time-code" maxLength={6} required value={otp} onChange={(event) => setOtp(event.target.value.replace(/\D/g, ''))} /></label>}
          {error && <p className="form-error" role="alert">{error}</p>}
          {hint && <p className="demo-note auth-hint"><CircleHelp size={14} /> {hint}</p>}
          <button className="button button-primary login-submit" type="submit" disabled={submitting}>{submitting ? 'Проверка…' : codeRequested ? 'Подтвердить вход' : 'Запросить код'} <ArrowRight size={17} /></button>
          {!codeRequested && <p className="demo-note"><CircleHelp size={14} /> Для демонстрации используйте мастер-код 123456.</p>}
          {codeRequested && !offlineDemo && <button className="clear-button resend-code" type="button" onClick={() => { setCodeRequested(false); setHint(''); setError('') }}>Изменить email</button>}
        </form>
        <div className="auth-foot"><span>Демо-контур · вход по email</span><span>Защищённая сессия <i /></span></div>
      </section>
      <aside className="auth-visual" aria-label="Геоаналитическая карта региона">
        <div className="visual-grid" />
        <div className="visual-top"><span>РЫНОК В ФОКУСЕ</span><span>47°13′ N&nbsp;&nbsp; 39°42′ E</span></div>
        <div className="visual-orbit orbit-one" /><div className="visual-orbit orbit-two" />
        <div className="visual-cross cross-one" /><div className="visual-cross cross-two" />
        <div className="visual-map-label label-a"><span /> Ростов-на-Дону <small>18 компаний</small></div>
        <div className="visual-map-label label-b"><span /> Аксай <small>6 возможностей</small></div>
        <div className="visual-caption"><span>01 / 03</span><strong>Данные становятся<br />коммерческим преимуществом.</strong><small>Открытые источники · аналитика · действие</small></div>
      </aside>
    </main>
  )
}

function Header({ active, onChange, onLogout }: { active: Module; onChange: (value: Module) => void; onLogout: () => void }) {
  return (
    <header className="app-header">
      <Brand />
      <nav className="module-tabs" aria-label="Модули">
        {modules.map(({ id, label, icon: Icon }, index) => (
          <button className={`module-tab ${active === id ? 'active' : ''}`} key={id} onClick={() => onChange(id)}>
            <Icon size={17} strokeWidth={1.8} /><span>{label}</span><small>0{index + 1}</small>
          </button>
        ))}
      </nav>
      <div className="header-user"><span className="user-avatar">МС</span><div><strong>Мария Соколова</strong><small>Коммерческий блок</small></div><button className="icon-button logout-button" title="Выйти" aria-label="Выйти" onClick={onLogout}><LogOut size={17} /></button></div>
    </header>
  )
}

function PageHeading({ kicker, title, detail, action }: { kicker: string; title: string; detail: string; action?: ReactNode }) {
  return <div className="page-heading"><div><span className="eyebrow">{kicker}</span><h1>{title}</h1><p>{detail}</p></div>{action}</div>
}

function Metric({ label, value, note, icon: Icon, accent = '' }: { label: string; value: string; note: string; icon: typeof Building2; accent?: string }) {
  return <article className="metric"><span className={`metric-icon ${accent}`}><Icon size={17} /></span><div><span className="metric-label">{label}</span><strong>{value}</strong><small>{note}</small></div></article>
}

function CompanyCard({ company, onEstimate }: { company: Company; onEstimate: (company: Company) => void }) {
  return (
    <section className="selection-card">
      <div className="selection-top"><span className="eyebrow">ВЫБРАННАЯ КОМПАНИЯ</span></div>
      <h3>{company.name}</h3>
      <span className="company-industry">{company.industry} <span>·</span> ИНН {company.inn}</span>
      <div className="company-revenue"><span>Выручка за год <small className="estimate-label">оценка</small></span><strong>{formatMoney(company.revenue)}<small> млн ₽</small></strong></div>
      <div className={`growth ${company.growth < 0 ? 'negative' : ''}`}>{company.growth < 0 ? <TrendingDown size={15} /> : <TrendingUp size={15} />}{company.growth > 0 ? '+' : ''}{company.growth}% <span>динамика</span></div>
      <div className="company-address"><MapPin size={14} />{company.address}</div>
      <button className="text-action" onClick={() => onEstimate(company)}>Оценить проект <ArrowRight size={15} /></button>
    </section>
  )
}

function Radar({ data, region, allowServerExport, onEstimate }: { data: Company[]; region: string; allowServerExport: boolean; onEstimate: (company: Company) => void }) {
  const [query, setQuery] = useState('')
  const [industry, setIndustry] = useState('Все отрасли')
  const [minRevenue, setMinRevenue] = useState(0)
  const [maxRevenue, setMaxRevenue] = useState('')
  const [whiteSpots, setWhiteSpots] = useState(true)
  const [heatmap, setHeatmap] = useState(true)
  const [selectedId, setSelectedId] = useState(1)
  const filtered = useMemo(() => data.filter((company) => {
    const matchesQuery = `${company.name} ${company.inn}`.toLowerCase().includes(query.toLowerCase())
    const belowMax = maxRevenue === '' || company.revenue <= Number(maxRevenue)
    return matchesQuery && (industry === 'Все отрасли' || company.industry === industry) && company.revenue >= minRevenue && belowMax
  }), [data, query, industry, minRevenue, maxRevenue])
  const selected = filtered.find((company) => company.id === selectedId) ?? filtered[0]
  const whiteSpotZones = useMemo(() => {
    const totals = new Map<string, { revenue: number; clients: number; markedSpot: boolean }>()
    data.forEach((company) => {
      const zone = totals.get(company.zone) ?? { revenue: 0, clients: 0, markedSpot: false }
      zone.revenue += company.revenue
      zone.clients += Number(company.client)
      zone.markedSpot ||= Boolean(company.whiteSpot)
      totals.set(company.zone, zone)
    })
    return new Set([...totals].filter(([, zone]) => zone.clients === 0 && zone.revenue >= 300 && zone.markedSpot).map(([name]) => name))
  }, [data])
  const points = filtered.map((company) => ({
    id: company.id, name: company.name, lat: company.lat, lon: company.lon,
    color: '#7028d8',
    detail: company.industry,
    weight: company.revenue,
    whiteSpot: whiteSpots && (whiteSpotZones.has(company.zone) || Boolean(company.whiteSpot)),
  }))
  const estimatedRevenue = filtered.reduce((sum, company) => sum + company.revenue, 0)

  async function exportCsv() {
    const canExportServerSelection = allowServerExport && !query && minRevenue === 0 && !maxRevenue
    const serverFile = canExportServerSelection ? await exportCompaniesCsv({
      ...(industry !== 'Все отрасли' ? { industry } : {}),
    }) : null
    const header = ['Название', 'ИНН', 'Отрасль', 'Оценочная выручка, млн руб.', 'Рост, %', 'Адрес']
    const rows = filtered.map((company) => [company.name, company.inn, company.industry, company.revenue, company.growth, company.address])
    const csv = [header, ...rows].map((row) => row.map((value) => `"${String(value).replace(/"/g, '""')}"`).join(';')).join('\n')
    const url = URL.createObjectURL(serverFile ?? new Blob(['\uFEFF', csv], { type: 'text/csv;charset=utf-8' }))
    const link = Object.assign(document.createElement('a'), { href: url, download: 'rtk-leads-export.csv' })
    link.click()
    window.setTimeout(() => URL.revokeObjectURL(url), 1000)
  }

  return (
    <>
      <PageHeading kicker="МОДУЛЬ 01 · РЫНОК И ПОКРЫТИЕ" title="Радар присутствия" detail="Найдите компании с потенциалом роста и оцените покрытие региона." action={<button className="button button-outline" onClick={exportCsv}><ArrowDownToLine size={16} /> Экспорт CSV <span className="button-count">{filtered.length}</span></button>} />
      <div className="metric-row">
        <Metric label="Компаний в выборке" value={String(filtered.length).padStart(2, '0')} note="в текущем срезе" icon={Building2} />
        <Metric label="Оценочная выручка" value={`${formatMoney(estimatedRevenue)} млн`} note="в текущей выборке" icon={Wallet} accent="orange" />
        <Metric label="Белые пятна" value={String(whiteSpotZones.size).padStart(2, '0')} note="зоны высокой активности" icon={MapPin} accent="green" />
        <Metric label="Динамика рынка" value="+14,8%" note="год к году · выборка" icon={TrendingUp} accent="blue" />
      </div>
      <div className="radar-layout">
        <aside className="filter-panel">
          <div className="panel-heading"><div><SlidersHorizontal size={17} /><strong>Фильтры</strong></div><button className="clear-button" onClick={() => { setQuery(''); setIndustry('Все отрасли'); setMinRevenue(0); setMaxRevenue('') }}>Сбросить</button></div>
          <label className="search-field"><Search size={16} /><input placeholder="Компания или ИНН" value={query} onChange={(event) => setQuery(event.target.value)} /></label>
          <label className="field-label">Отрасль<select value={industry} onChange={(event) => setIndustry(event.target.value)}><option>Все отрасли</option>{industries.map((item) => <option key={item}>{item}</option>)}</select><ChevronDown size={14} /></label>
          <div className="revenue-range"><span>Выручка, млн ₽ <small>оценка</small></span><div className="revenue-range-inputs"><label>от<input type="number" min="0" value={minRevenue || ''} placeholder="0" onChange={(event) => setMinRevenue(Math.max(0, Number(event.target.value) || 0))} /></label><label>до<input type="number" min={minRevenue} value={maxRevenue} placeholder="без лимита" onChange={(event) => setMaxRevenue(event.target.value)} /></label></div></div>
          <label className="check-row white-toggle"><input type="checkbox" checked={whiteSpots} onChange={(event) => setWhiteSpots(event.target.checked)} /><span className="custom-check"><Check size={12} /></span><span>Подсветить белые пятна</span><span className="orange-dot" /></label>
          <label className="check-row heat-toggle"><input type="checkbox" checked={heatmap} onChange={(event) => setHeatmap(event.target.checked)} /><span className="custom-check"><Check size={12} /></span><span>Тепловой слой выручки</span><span className="heat-dot" /></label>
          <div className="filter-foot"><Filter size={14} /> Обновлено сегодня, 09:42</div>
        </aside>
        <section className="map-panel">
          <div className="map-head"><div><strong>{region}</strong><span><span className="map-live" /> {data === demoCompanies ? 'Демо-данные' : 'Данные API'} · {filtered.length} компаний</span></div><button className="map-expand" title="Карта интерактивна" aria-label="Интерактивная карта"><MapPin size={17} /></button></div>
          <div className="map-canvas"><GeoMap points={points} selectedId={selected?.id ?? -1} center={selected ? [selected.lat, selected.lon] : [47.2225, 39.7187]} onSelect={setSelectedId} heatmap={heatmap} />
            <div className="map-legend">{whiteSpots && <span><i className="legend-white" /> Белые пятна</span>}<span><i className="legend-density" /> Плотность выручки</span></div>
            <div className="map-scale">OpenStreetMap</div>
          </div>
          <div className="map-foot"><span><BadgeCheck size={14} /> Зоны рассчитаны по плотности лидов и выручке</span><span>{data === demoCompanies ? 'Схематичные демо-данные' : 'Источник: реестр компаний API'}</span></div>
        </section>
        {selected ? <CompanyCard company={selected} onEstimate={onEstimate} /> : <div className="selection-card empty-selection"><Search size={22} /><strong>Ничего не найдено</strong><span>Измените фильтры, чтобы увидеть компании.</span></div>}
      </div>
      <div className="result-strip"><span>КОМПАНИИ В ЗОНЕ</span><div className="result-pills">{filtered.slice(0, 5).map((company) => <button key={company.id} className={company.id === selected?.id ? 'selected' : ''} onClick={() => setSelectedId(company.id)}>{company.name}</button>)}</div><span className="result-more">{filtered.length > 5 ? `+ ещё ${filtered.length - 5}` : 'Все результаты'}</span></div>
    </>
  )
}

function Investment({ data, region, onEstimate }: { data: InvestProject[]; region: string; onEstimate: (project: InvestProject) => void }) {
  const [stage, setStage] = useState('Все стадии')
  const [selectedId, setSelectedId] = useState(demoProjects[0].id)
  const filtered = data.filter((project) => stage === 'Все стадии' || project.stage === stage)
  const selected = filtered.find((project) => project.id === selectedId) ?? filtered[0]
  const points = filtered.map((project) => ({ id: project.id, name: project.title, lat: project.lat, lon: project.lon, color: project.stage === 'Строительство' ? '#ff5a36' : project.stage === 'Запуск' ? '#6a24d9' : '#2a9a7b', detail: project.stage }))
  return (
    <>
      <PageHeading kicker="МОДУЛЬ 02 · КАПИТАЛЬНЫЕ ВЛОЖЕНИЯ" title="Инвест-навигатор" detail="Будущие стройки и модернизации — новые точки входа в рынок." action={<label className="select-action"><CalendarDays size={16} /><select value={stage} onChange={(event) => setStage(event.target.value)}><option>Все стадии</option><option>Проектирование</option><option>Строительство</option><option>Запуск</option></select><ChevronDown size={14} /></label>} />
      <div className="metric-row invest-metrics">
        <Metric label="Активных проектов" value={String(filtered.length).padStart(2, '0')} note={`в регионе: ${region}`} icon={Layers3} />
        <Metric label="Объём инвестиций" value={`${formatMoney(filtered.reduce((sum, item) => sum + item.budget, 0))} млн`} note="совокупный бюджет" icon={Wallet} accent="orange" />
        <Metric label="Ближайшее событие" value={selected ? new Date(`${selected.date}T00:00:00`).toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' }) : '—'} note={selected?.title ?? 'Нет событий'} icon={CalendarDays} accent="blue" />
      </div>
      <div className="invest-layout">
        <section className="timeline-panel">
          <div className="panel-heading"><div><CalendarDays size={17} /><strong>События и проекты</strong></div><span className="timeline-count">{filtered.length} объекта</span></div>
          <div className="timeline-list">
            {filtered.map((project) => (
              <button key={project.id} className={`timeline-item ${selected?.id === project.id ? 'active' : ''}`} onClick={() => setSelectedId(project.id)}>
                <span className={`timeline-marker ${project.stage === 'Строительство' ? 'stage-build' : project.stage === 'Запуск' ? 'stage-launch' : 'stage-plan'}`} />
                <span className="timeline-date">{new Date(`${project.date}T00:00:00`).toLocaleDateString('ru-RU', { day: '2-digit', month: 'short', year: 'numeric' })}</span>
                <strong>{project.title}</strong><span className="timeline-investor">{project.investor} · {project.industry}</span>
                <span className={`stage-tag ${project.stage === 'Строительство' ? 'build' : project.stage === 'Запуск' ? 'launch' : 'plan'}`}>{project.stage}</span>
              </button>
            ))}
            {!filtered.length && <div className="empty-state">На этой стадии проектов пока нет.</div>}
          </div>
          <div className="timeline-legend"><span><i className="stage-plan-dot" /> Проектирование</span><span><i className="stage-build-dot" /> Строительство</span><span><i className="stage-launch-dot" /> Запуск</span></div>
        </section>
        <section className="invest-map-panel">
          <div className="map-head"><div><strong>Объекты региона</strong><span>Выберите событие для перехода к объекту</span></div><span className="map-live" /></div>
          <div className="invest-map"><GeoMap points={points} selectedId={selected?.id ?? -1} center={selected ? [selected.lat, selected.lon] : [47.2225, 39.7187]} onSelect={setSelectedId} clusterAtZoom={12} /></div>
          {selected ? <div className="project-detail"><div><span className="eyebrow">{selected.investor} · {selected.stage.toUpperCase()}</span><h3>{selected.title}</h3><p>{selected.description}</p><div className="need-tags">{selected.needs.map((need) => <span key={need}>{need}</span>)}</div></div><div className="project-budget"><span>Инвестиции</span><strong>{formatMoney(selected.budget)}<small> млн ₽</small></strong><span>Событие {new Date(`${selected.date}T00:00:00`).toLocaleDateString('ru-RU')}</span><button className="text-action project-evaluate" onClick={() => onEstimate(selected)}>Оценить проект <ArrowRight size={14} /></button></div></div> : <div className="empty-state">Выберите проект в списке.</div>}
        </section>
      </div>
    </>
  )
}

const equipmentOptions = [
  { id: 'fiber_optics', label: 'Оптическая сеть', price: 520000 },
  { id: 'telephony', label: 'IP-телефония', price: 340000 },
  { id: 'cctv', label: 'Видеонаблюдение', price: 680000 },
  { id: 'data_center', label: 'Серверная и СХД', price: 890000 },
  { id: 'access_control', label: 'СКУД', price: 210000 },
]
const objectFactors: Record<string, number> = { 'Складской комплекс': 1.18, 'Производственная площадка': 1.35, 'Офисный центр': 0.92 }
const scaleFactors: Record<string, number> = { 'До 5 000 м²': 0.78, '5 000–20 000 м²': 1, 'Более 20 000 м²': 1.42 }
const scaleValues: Record<string, number> = { 'До 5 000 м²': 4000, '5 000–20 000 м²': 12500, 'Более 20 000 м²': 25000 }

function CalculatorModule({ selectedCompany, selectedProject, companiesAreApi, projectsAreApi }: { selectedCompany: Company | null; selectedProject: InvestProject | null; companiesAreApi: boolean; projectsAreApi: boolean }) {
  const [objectType, setObjectType] = useState('Складской комплекс')
  const [scale, setScale] = useState('5 000–20 000 м²')
  const [duration, setDuration] = useState(3)
  const [selectedEquipment, setSelectedEquipment] = useState(['fiber_optics', 'cctv', 'data_center'])
  const [customer, setCustomer] = useState(selectedCompany?.name ?? selectedProject?.investor ?? '')
  const [notice, setNotice] = useState('')
  const [serverEstimate, setServerEstimate] = useState<DealEstimate | null>(null)
  const equipment = equipmentOptions.filter((item) => selectedEquipment.includes(item.id))
  const equipmentCost = equipment.reduce((sum, item) => sum + item.price, 0)
  const urgencyFactor = duration < 3 ? 1.18 : duration > 6 ? 0.96 : 1
  const localTotal = Math.round((equipmentCost + 540000) * objectFactors[objectType] * scaleFactors[scale] * urgencyFactor)
  const total = serverEstimate?.optimal_price ?? Math.round(localTotal * 1.12)
  const costPrice = serverEstimate?.cost_price ?? Math.round(localTotal * 0.76)
  const install = Math.round(costPrice * 0.3)
  const licenses = Math.round(costPrice * 0.1)
  const equipmentTotal = costPrice - install - licenses
  const minPrice = serverEstimate?.min_price ?? Math.round(localTotal * 0.87)
  const optimalPrice = serverEstimate?.optimal_price ?? Math.round(localTotal * 1.12)
  const recommendedMargin = serverEstimate?.margin_percent ?? 24.5
  const costs = [{ name: 'Оборудование', value: equipmentTotal, color: '#7028d8' }, { name: 'Монтаж', value: install, color: '#ff653f' }, { name: 'Лицензии', value: licenses, color: '#39a58c' }]
  const benchmarks = [
    ...(serverEstimate?.benchmarks.map((benchmark) => ({ name: benchmark.title, price: benchmark.price / 1_000_000 })) ?? [
      { name: 'Малая площадка', price: total * 0.62 / 1_000_000 },
      { name: 'Аналог 01', price: total * 0.91 / 1_000_000 },
      { name: 'Аналог 02', price: total * 1.07 / 1_000_000 },
    ]),
    { name: 'Ваш проект', price: optimalPrice / 1_000_000 },
  ]
  const benchmarkChartData = benchmarks.map((benchmark, index) => ({
    ...benchmark,
    axisLabel: benchmark.name === 'Ваш проект' ? 'Ваш проект' : `Аналог ${index + 1}`,
  }))
  const similarBenchmarks = serverEstimate?.benchmarks ?? []
  const similarCount = serverEstimate ? similarBenchmarks.length : 4
  const similarMin = similarBenchmarks.length ? Math.min(...similarBenchmarks.map((deal) => deal.price)) : Math.round(total * 0.62)
  const similarMax = similarBenchmarks.length ? Math.max(...similarBenchmarks.map((deal) => deal.price)) : Math.round(total * 1.07)

  useEffect(() => {
    let current = true
    setServerEstimate(null)
    const urgency = duration < 3 ? 1.2 : duration > 8 ? 0.9 : 1
    calculateDeal({
      ...(selectedCompany && companiesAreApi ? { company_id: selectedCompany.id } : {}),
      ...(selectedProject && projectsAreApi ? { project_id: selectedProject.id } : {}),
      scale_param: scaleValues[scale],
      work_types: selectedEquipment,
      urgency_coeff: urgency,
      region_coeff: 1.05,
    }).then((estimate) => { if (current) setServerEstimate(estimate) })
    return () => { current = false }
  }, [objectType, scale, duration, selectedEquipment, selectedCompany, selectedProject, companiesAreApi, projectsAreApi])

  function toggleEquipment(id: string) {
    setSelectedEquipment((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id])
  }

  async function generateProposal() {
    setNotice('')
    const payload = {
      ...(selectedCompany && companiesAreApi ? { company_id: selectedCompany.id } : {}),
      ...(selectedProject && projectsAreApi ? { project_id: selectedProject.id } : {}),
      scale_param: scaleValues[scale],
      work_types: selectedEquipment,
      urgency_coeff: duration < 3 ? 1.2 : duration > 8 ? 0.9 : 1,
      region_coeff: 1.05,
    }
    const serverFile = await generateProposalDoc(payload)
    if (serverFile) {
      const url = URL.createObjectURL(serverFile)
      const link = Object.assign(document.createElement('a'), { href: url, download: 'KP_Rostelecom_Deal.docx' })
      link.click()
      window.setTimeout(() => URL.revokeObjectURL(url), 1000)
      setNotice('Коммерческое предложение сформировано.')
      return
    }
    const doc = new Document({ sections: [{ children: [
      new Paragraph({ text: 'РОСТЕЛЕКОМ', heading: HeadingLevel.HEADING_1 }),
      new Paragraph({ text: 'Коммерческое предложение', heading: HeadingLevel.TITLE }),
      new Paragraph({ children: [new TextRun({ text: `Заказчик: ${customer.trim() || 'Не указан'}`, bold: true })] }),
      new Paragraph(`Объект: ${objectType}`),
      new Paragraph(`Масштаб: ${scale}; срок реализации: ${duration} мес.`),
      new Paragraph({ text: 'Состав предложения', heading: HeadingLevel.HEADING_2 }),
      ...equipment.map((item) => new Paragraph({ text: `${item.label} — ${formatMoney(item.price)} руб.`, bullet: { level: 0 } })),
      new Paragraph({ text: `Минимальная стоимость: ${formatMoney(minPrice)} руб.` }),
      new Paragraph({ children: [new TextRun({ text: `Рекомендуемая стоимость: ${formatMoney(optimalPrice)} руб.`, bold: true })] }),
      new Paragraph(`Рекомендуемая маржа: ${recommendedMargin}%.`),
      new Paragraph({ children: [new TextRun({ text: 'Демо-документ сформирован для предварительной оценки.', italics: true })] }),
    ] }] })
    try {
      const blob = await Packer.toBlob(doc)
      const url = URL.createObjectURL(blob)
      const link = Object.assign(document.createElement('a'), { href: url, download: 'KP_Rostelecom_Deal.docx' })
      link.click()
      URL.revokeObjectURL(url)
      setNotice('Коммерческое предложение сформировано.')
    } catch {
      setNotice('Не удалось сформировать документ. Попробуйте ещё раз.')
    }
  }

  return (
    <>
      <PageHeading kicker="МОДУЛЬ 03 · ПРЕДВАРИТЕЛЬНАЯ ОЦЕНКА" title="Калькулятор сделок" detail="Соберите спецификацию проекта и получите ценовой ориентир для КП." action={<span className="benchmark-badge"><span /> {serverEstimate ? 'Исторические сделки из API' : 'Демо-аналоги'}</span>} />
      <div className="calculator-layout">
        <section className="calculator-form panel">
          <div className="panel-heading"><div><SlidersHorizontal size={17} /><strong>Параметры проекта</strong></div><span className="step-label">01 / 03</span></div>
          <label className="input-group">Тип объекта<select value={objectType} onChange={(event) => setObjectType(event.target.value)}><option>Складской комплекс</option><option>Производственная площадка</option><option>Офисный центр</option></select><ChevronDown size={14} /></label>
          <label className="input-group">Масштаб объекта<select value={scale} onChange={(event) => setScale(event.target.value)}><option>До 5 000 м²</option><option>5 000–20 000 м²</option><option>Более 20 000 м²</option></select><ChevronDown size={14} /></label>
          <div className="range-label duration-label"><label htmlFor="duration">Срок реализации</label><strong>{duration} мес.</strong></div>
          <input id="duration" className="range-input" type="range" min="1" max="12" value={duration} onChange={(event) => setDuration(Number(event.target.value))} />
          <div className="range-scale"><span>1 мес.</span><span>12 мес.</span></div>
          <div className="equipment-heading"><span>Состав работ и оборудования</span><small>{selectedEquipment.length} выбрано</small></div>
          <div className="equipment-list">{equipmentOptions.map((item) => <label className="equipment-option" key={item.id}><input type="checkbox" checked={selectedEquipment.includes(item.id)} onChange={() => toggleEquipment(item.id)} /><span className="custom-check"><Check size={12} /></span><span>{item.label}</span><small>{formatMoney(item.price)} ₽</small></label>)}</div>
          <label className="input-group customer-input">Название заказчика<input value={customer} onChange={(event) => setCustomer(event.target.value)} placeholder="Например, ООО «Вектор»" /></label>
        </section>
        <section className="estimate-column">
          <div className="estimate-topline"><span>ОРИЕНТИР СТОИМОСТИ ПРОЕКТА</span><span className="live-calc"><i /> {serverEstimate ? 'Расчёт API' : 'Демо-расчёт'}</span></div>
          <div className="price-cards"><article className="price-card"><span>Минимальная цена</span><strong>{formatMoney(minPrice)}<small>₽</small></strong><small>базовая комплектация</small></article><article className="price-card featured"><span>Рекомендуемая цена</span><strong>{formatMoney(optimalPrice)}<small>₽</small></strong><small><TrendingUp size={13} /> маржа {recommendedMargin}%</small></article></div>
          <div className="charts-row">
            <section className="chart-panel"><div className="chart-title"><strong>Структура сметы</strong><small>распределение себестоимости</small></div><div className="pie-area"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={costs} dataKey="value" nameKey="name" innerRadius={52} outerRadius={72} paddingAngle={3} stroke="none">{costs.map((item) => <Cell key={item.name} fill={item.color} />)}</Pie><Tooltip formatter={(value) => `${formatMoney(Number(value))} ₽`} /></PieChart></ResponsiveContainer><div className="pie-center"><span>СЕБЕСТОИМОСТЬ</span><strong>{formatMoney(costPrice)}</strong><small>₽</small></div></div><div className="chart-legend">{costs.map((item) => <span key={item.name}><i style={{ backgroundColor: item.color }} />{item.name}<small>{Math.round(item.value / costPrice * 100)}%</small></span>)}</div></section>
            <section className="chart-panel benchmark-chart"><div className="chart-title"><strong>Сравнение с аналогами</strong><small>стоимость проекта, млн ₽</small></div><div className="bar-area"><ResponsiveContainer width="100%" height="100%"><BarChart data={benchmarkChartData} margin={{ top: 8, right: 6, left: -20, bottom: 0 }}><CartesianGrid vertical={false} stroke="#ecebf1" /><XAxis dataKey="axisLabel" tick={{ fontSize: 9, fill: '#77798a' }} axisLine={false} tickLine={false} interval={0} /><YAxis tick={{ fontSize: 9, fill: '#77798a' }} axisLine={false} tickLine={false} /><Tooltip labelFormatter={(label) => benchmarkChartData.find((item) => item.axisLabel === label)?.name ?? label} formatter={(value) => `${formatMoney(Number(value))} млн ₽`} /><Bar dataKey="price" radius={[4, 4, 0, 0]}>{benchmarkChartData.map((item) => <Cell key={item.name} fill={item.name === 'Ваш проект' ? '#ff653f' : '#a58ad8'} />)}</Bar></BarChart></ResponsiveContainer></div></section>
          </div>
          <div className="estimate-bottom"><div className="similar-deals"><span className="similar-icon"><Building2 size={16} /></span><div><strong>{similarCount} похожие сделки</strong><small>{serverEstimate ? 'исторические сделки backend' : 'демо-аналоги'}</small></div><span className="similar-range">{formatMoney(similarMin)} – {formatMoney(similarMax)} ₽</span></div><button className="button button-primary proposal-button" onClick={generateProposal}><FileText size={16} /> Сформировать КП <ArrowRight size={16} /></button></div>
          {notice && <div className="notice" role="status">{notice}</div>}
        </section>
      </div>
    </>
  )
}

export default function App() {
  const [token, setToken] = useState(initialToken)
  const [active, setActive] = useState<Module>('radar')
  const [companies, setCompanies] = useState(demoCompanies)
  const [projects, setProjects] = useState(demoProjects)
  const [source, setSource] = useState('DEMO-ДАННЫЕ')
  const [companiesAreApi, setCompaniesAreApi] = useState(false)
  const [projectsAreApi, setProjectsAreApi] = useState(false)
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null)
  const [selectedProject, setSelectedProject] = useState<InvestProject | null>(null)
  const region = 'Ростовская область'

  useEffect(() => {
    if (!token) {
      setCompanies(demoCompanies)
      setProjects(demoProjects)
      setCompaniesAreApi(false)
      setProjectsAreApi(false)
      setSource('DEMO-ДАННЫЕ')
      return
    }
    let activeRequest = true
    Promise.all([loadCompanies(), loadProjects()]).then(([companyResult, projectResult]) => {
      if (!activeRequest) return
      const regionalCompanies = companyResult.data.filter((company) => isInRostovRegion(company.lat, company.lon))
      const regionalProjects = projectResult.data.filter((project) => isInRostovRegion(project.lat, project.lon))
      const hasApiCompanies = companyResult.source === 'api' && regionalCompanies.length > 0
      const hasApiProjects = projectResult.source === 'api' && regionalProjects.length > 0
      setCompanies(hasApiCompanies ? regionalCompanies : demoCompanies)
      setProjects(hasApiProjects ? regionalProjects : demoProjects)
      setCompaniesAreApi(hasApiCompanies)
      setProjectsAreApi(hasApiProjects)
      setSource(hasApiCompanies && hasApiProjects ? 'API' : hasApiCompanies || hasApiProjects ? 'API + демо-регион' : 'ДЕМО-ДАННЫЕ')
    })
    return () => { activeRequest = false }
  }, [token])

  useEffect(() => {
    const expireSession = () => setToken(null)
    window.addEventListener('api-auth-expired', expireSession)
    return () => window.removeEventListener('api-auth-expired', expireSession)
  }, [])

  if (!token) return <Login onLogin={setToken} />

  function logout() {
    window.localStorage.removeItem('rtk-demo-token')
    setToken(null)
  }

  return (
    <div className="app-shell">
      <Header active={active} onChange={setActive} onLogout={logout} />
      <main className="workspace">
        <div className="workspace-topline"><span>{region.toLocaleUpperCase('ru-RU')} <i /> РЫНОК И ИНВЕСТИЦИИ</span><span><span className="sync-dot" />{source} · Данные обновлены 24 октября 2026</span></div>
        {active === 'radar' && <Radar data={companies} region={region} allowServerExport={companiesAreApi} onEstimate={(company) => { setSelectedCompany(company); setSelectedProject(null); setActive('calculator') }} />}
        {active === 'invest' && <Investment data={projects} region={region} onEstimate={(project) => { setSelectedProject(project); setSelectedCompany(null); setActive('calculator') }} />}
        {active === 'calculator' && <CalculatorModule selectedCompany={selectedCompany} selectedProject={selectedProject} companiesAreApi={companiesAreApi} projectsAreApi={projectsAreApi} />}
        <footer className="app-footer"><span>КОНТУР <span>·</span> {source}</span><span>{source.includes('API') ? 'API подключен; на карте только данные Ростовской области' : 'Региональные данные синтетические и предназначены для демонстрации'}</span></footer>
      </main>
    </div>
  )
}