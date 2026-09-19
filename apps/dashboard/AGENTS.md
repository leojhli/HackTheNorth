# figma-make-app

React + Vite + Tailwind CSS project exported from Figma Make and connected to the BeProgram API in this checkout.

## Development Server

The export originally assumed Figma's pre-running `$PORT` server. That does not apply to this local checkout.

- See the root README for local setup; FastAPI serves the built site on port 8000.
- `npm run dev` starts Vite on 127.0.0.1:5173 with the API proxy. Run the API separately.
- Do not reintroduce the prototype's timer/fixture evaluator into production navigation.

## Project Structure

This is the canonical project structure. Start with task-relevant files below. Only follow imports or inspect other files when required, when a documented path is missing, or when the repository contradicts this guide.

- `src/main.tsx` - React entrypoint; imports `src/index.css` and mounts `src/LiveApp.tsx` into the `#root` element
- `src/LiveApp.tsx` - Live authentication, state reconciliation, routing and API orchestration
- `src/App.tsx` - Preserved prototype reference only; contains simulated behavior and is not a production entrypoint
- `src/index.css` - Global CSS entrypoint and Tailwind CSS v4 import
- `index.html` - Vite HTML shell containing the `#root` element and loading `src/main.tsx`
- `package.json` - Project dependencies and the Vite build, development, preview, and formatting scripts
- `vite.config.ts` - Vite configuration with React, Tailwind CSS v4, and Figma Make plugins plus the `@` alias for `src`
- `.mise.toml` - Toolchain versions for Node.js and pnpm

## Dependencies

- Runtime: React 19 and React DOM 19
- Styling: Tailwind CSS v4 with the `@tailwindcss/vite` plugin
- Build tooling: Vite 8, TypeScript 5.7, and `@vitejs/plugin-react`
- Formatting: oxfmt

## Styling

This project uses **Tailwind CSS v4** through the `@tailwindcss/vite` plugin configured in `vite.config.ts`. `src/index.css` imports Tailwind with `@import 'tailwindcss';`. Use Tailwind utility classes directly in JSX and put global CSS or Tailwind v4 theme customization in `src/index.css`. This scaffold does not need a Tailwind config file or PostCSS config.

`src/main.tsx` imports `src/index.css`, so global font wiring belongs in `src/index.css`. Keep CSS `@import` statements first, then add any `@font-face` rules and font-family defaults there.
