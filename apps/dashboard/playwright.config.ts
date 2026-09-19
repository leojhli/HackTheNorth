import { defineConfig } from '@playwright/test'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')
const python = process.env.BEPROGRAM_TEST_PYTHON || path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python')
const port = Number(process.env.BEPROGRAM_E2E_PORT || 8020)
if (!Number.isInteger(port) || port < 1024 || port > 65535) throw Error('Invalid BEPROGRAM_E2E_PORT')
const origin = `http://127.0.0.1:${port}`
export default defineConfig({
  testDir: './tests', timeout: 40000, workers: 1, reporter: 'list',
  use: { baseURL:origin, browserName:'chromium', launchOptions: { executablePath: process.env.BEPROGRAM_BROWSER_EXECUTABLE }, viewport:{width:1440,height:1000}, screenshot:'only-on-failure', trace:'retain-on-failure' },
  webServer: { command:`"${python}" -m tests.e2e_server`, cwd:root, env:{BEPROGRAM_E2E_PORT:String(port)}, url:origin+'/health', timeout:30000, reuseExistingServer:false },
})
