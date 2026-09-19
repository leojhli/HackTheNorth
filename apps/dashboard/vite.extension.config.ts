import {defineConfig} from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'node:path'

export default defineConfig({
  define:{'process.env.NODE_ENV':JSON.stringify('production')},
  plugins:[
    {name:'local-webview-styles',enforce:'pre',transform(code,id){
      if(id.replaceAll('\\','/').endsWith('/src/index.css'))
        return code.replace(/^@import url\('https:\/\/fonts\.googleapis\.com[^;]+;\r?\n/gm,'')
    }},
    react(),tailwindcss()
  ],
  build:{
    outDir:'../vscode-extension/media',emptyOutDir:true,cssCodeSplit:false,
    lib:{entry:path.resolve(import.meta.dirname,'src/sidebar/main.tsx'),name:'BeProgramSidebar',formats:['iife'],fileName:()=> 'webview.js',cssFileName:'webview'},
    sourcemap:false
  }
})
