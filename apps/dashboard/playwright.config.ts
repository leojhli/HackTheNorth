import { defineConfig } from '@playwright/test'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')
const python = process.env.BEPROGRAM_TEST_PYTHON || path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python')
export default defineConfig({
  testDir: './tests', timeout: 40000, workers: 1, reporter: 'list',
  use: { baseURL:'http://127.0.0.1:8010', browserName:'chromium', launchOptions: { executablePath: process.env.BEPROGRAM_BROWSER_EXECUTABLE }, viewport:{width:1440,height:1000}, screenshot:'only-on-failure', trace:'retain-on-failure' },
  webServer: { command:`"${python}" -m tests.e2e_server`, cwd:root, url:'http://127.0.0.1:8010/health', timeout:30000, reuseExistingServer:false },
})
