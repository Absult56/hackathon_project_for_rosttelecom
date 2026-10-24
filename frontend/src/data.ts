export type Company = {
  id: number
  name: string
  inn: string
  industry: string
  revenue: number
  growth: number
  lat: number
  lon: number
  address: string
  client: boolean
  zone: string
}

export type InvestProject = {
  id: number
  title: string
  investor: string
  industry: string
  stage: 'Проектирование' | 'Строительство' | 'Запуск'
  budget: number
  date: string
  needs: string[]
  lat: number
  lon: number
  description: string
}

export const industries = ['АПК', 'Торговля', 'Производство', 'ТЭК', 'IT']

const initialCompanies: Company[] = [
  { id: 1, name: 'Донские элеваторы', inn: '6164001122', industry: 'АПК', revenue: 145.2, growth: 12.4, lat: 47.2225, lon: 39.7187, address: 'Ростов-на-Дону, ул. Береговая, 8', client: false, zone: 'Центр' },
  { id: 2, name: 'Ростовский порт', inn: '6167012405', industry: 'Торговля', revenue: 820.4, growth: 8.1, lat: 47.2061, lon: 39.7342, address: 'Ростов-на-Дону, ул. Береговая, 30', client: true, zone: 'Порт' },
  { id: 3, name: 'Южная аграрная компания', inn: '6168057721', industry: 'АПК', revenue: 268.7, growth: 16.8, lat: 47.2572, lon: 39.6991, address: 'Ростов-на-Дону, пр. Михаила Нагибина, 14', client: false, zone: 'Север' },
  { id: 4, name: 'Технопарк «Старт»', inn: '6163120087', industry: 'IT', revenue: 96.3, growth: 22.1, lat: 47.2314, lon: 39.7018, address: 'Ростов-на-Дону, ул. Социалистическая, 74', client: false, zone: 'Центр' },
  { id: 5, name: 'Донской металлоцентр', inn: '6165129130', industry: 'Производство', revenue: 540.1, growth: -2.6, lat: 47.1908, lon: 39.6552, address: 'Ростов-на-Дону, ул. Доватора, 148', client: true, zone: 'Запад' },
  { id: 6, name: 'Аксайский логистический узел', inn: '6102064133', industry: 'Торговля', revenue: 352.6, growth: 18.4, lat: 47.2692, lon: 39.8683, address: 'Аксай, ул. Новочеркасское шоссе, 2', client: false, zone: 'Восток' },
  { id: 7, name: 'ТЭК-Дон', inn: '6167104418', industry: 'ТЭК', revenue: 1104.8, growth: 6.5, lat: 47.1807, lon: 39.7404, address: 'Ростов-на-Дону, ул. Нансена, 103', client: true, zone: 'Юг' },
  { id: 8, name: 'Фабрика «Молочный берег»', inn: '6168035528', industry: 'Производство', revenue: 188.9, growth: 11.2, lat: 47.2783, lon: 39.7179, address: 'Ростов-на-Дону, ул. Орская, 31', client: false, zone: 'Север' },
  { id: 9, name: 'АгроТрейд Юг', inn: '6102049110', industry: 'АПК', revenue: 424.5, growth: 9.7, lat: 47.2513, lon: 39.8214, address: 'Аксай, ул. Промышленная, 5', client: false, zone: 'Восток' },
  { id: 10, name: 'Сеть магазинов «Поле»', inn: '6163041009', industry: 'Торговля', revenue: 74.8, growth: 3.9, lat: 47.2158, lon: 39.6812, address: 'Ростов-на-Дону, ул. Большая Садовая, 91', client: false, zone: 'Центр' },
  { id: 11, name: 'Ростовский кабельный завод', inn: '6165107724', industry: 'Производство', revenue: 688.3, growth: 14.2, lat: 47.1649, lon: 39.6921, address: 'Ростов-на-Дону, ул. 2-я Луговая, 12', client: true, zone: 'Юг' },
  { id: 12, name: 'Цифровой Дон', inn: '6163095204', industry: 'IT', revenue: 132.4, growth: 27.8, lat: 47.2362, lon: 39.7542, address: 'Ростов-на-Дону, ул. Текучёва, 139', client: false, zone: 'Центр' },
  { id: 13, name: 'Новороссийский зерновой терминал', inn: '2315118302', industry: 'АПК', revenue: 920.2, growth: 7.4, lat: 47.231, lon: 39.765, address: 'Ростов-на-Дону, ул. 1-я Луговая, 3', client: false, zone: 'Порт' },
  { id: 14, name: 'Энергия Юга', inn: '6164091887', industry: 'ТЭК', revenue: 305.7, growth: 5.3, lat: 47.1965, lon: 39.777, address: 'Ростов-на-Дону, ул. Малиновского, 54', client: false, zone: 'Юг' },
  { id: 15, name: 'Донская мебельная мануфактура', inn: '6165098763', industry: 'Производство', revenue: 126.1, growth: -1.2, lat: 47.2423, lon: 39.6648, address: 'Ростов-на-Дону, ул. Таганрогская, 181', client: false, zone: 'Запад' },
  { id: 16, name: 'АгроСнаб Ростов', inn: '6102024891', industry: 'АПК', revenue: 237.5, growth: 13.6, lat: 47.2871, lon: 39.8452, address: 'Аксай, ул. Заречная, 7', client: true, zone: 'Восток' },
  { id: 17, name: 'Бизнес-центр «Сфера»', inn: '6163162086', industry: 'Торговля', revenue: 198.2, growth: 4.8, lat: 47.2292, lon: 39.7333, address: 'Ростов-на-Дону, ул. Красноармейская, 170', client: false, zone: 'Центр' },
  { id: 18, name: 'Инжиниринг Дон', inn: '6167120301', industry: 'IT', revenue: 82.7, growth: 31.4, lat: 47.1744, lon: 39.7202, address: 'Ростов-на-Дону, ул. Портовая, 80', client: false, zone: 'Юг' },
]

const demoZones = ['Центр', 'Север', 'Восток', 'Юг', 'Запад', 'Порт', 'Батайск', 'Новый Аксай']
const generatedCompanies: Company[] = Array.from({ length: 96 }, (_, index) => {
  const industry = industries[index % industries.length]
  const zone = demoZones[index % demoZones.length]
  return {
    id: 100 + index,
    name: `Демо-компания ${String(index + 1).padStart(3, '0')}`,
    inn: String(5000000000 + index),
    industry,
    revenue: 25 + (index * 53) % 850,
    growth: ((index * 17) % 31) - 6,
    lat: 47.11 + (index % 15) * 0.012,
    lon: 39.57 + (Math.floor(index / 15) % 12) * 0.026,
    address: `Ростовская область, демо-адрес ${index + 1}`,
    client: !['Батайск', 'Новый Аксай'].includes(zone) && index % 7 === 0,
    zone,
  }
})

export const companies: Company[] = [...initialCompanies, ...generatedCompanies]

export const projects: InvestProject[] = [
  { id: 101, title: 'Логистический хаб «Север»', investor: 'Логистик Групп', industry: 'Торговля', stage: 'Строительство', budget: 350, date: '2026-11-15', needs: ['Связь', 'Видеонаблюдение', 'СКУД'], lat: 47.2692, lon: 39.8683, description: 'Распределительный центр класса A с цифровым управлением складом.' },
  { id: 102, title: 'Модернизация «ДонМолоко»', investor: 'ДонМолоко', industry: 'АПК', stage: 'Проектирование', budget: 185, date: '2026-12-02', needs: ['IT-инфраструктура', 'АСУ ТП'], lat: 47.2783, lon: 39.7179, description: 'Расширение производственной площадки и запуск автоматизированной линии.' },
  { id: 103, title: 'Технопарк «Южный»', investor: 'Корпорация развития', industry: 'IT', stage: 'Запуск', budget: 620, date: '2027-01-20', needs: ['Связь', 'IT-инфраструктура', 'Видеонаблюдение'], lat: 47.2314, lon: 39.7018, description: 'Площадка для технологических компаний с готовой цифровой инфраструктурой.' },
  { id: 104, title: 'Энергоузел Восточный', investor: 'Энергия Юга', industry: 'ТЭК', stage: 'Строительство', budget: 480, date: '2027-02-10', needs: ['АСУ ТП', 'Связь', 'Видеонаблюдение'], lat: 47.1965, lon: 39.777, description: 'Новая подстанция и диспетчерский комплекс для растущего района.' },
]

export const formatMoney = (value: number) => new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 }).format(value)