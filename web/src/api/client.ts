import createClient from 'openapi-fetch'

import type { paths } from './schema'

// По умолчанию — прокси /api (vite dev / nginx). Для мока: VITE_API_URL=http://localhost:4010
export const api = createClient<paths>({ baseUrl: import.meta.env.VITE_API_URL ?? '/api' })
