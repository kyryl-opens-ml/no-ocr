/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SUPABASE_URL: string
  readonly VITE_SUPABASE_ANON_KEY: string
  readonly RAILWAY_TOKEN: string
  readonly MODAL_TOKEN_ID: string
  readonly MODAL_TOKEN_SECRET: string
  readonly VITE_REACT_APP_API_URI: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}