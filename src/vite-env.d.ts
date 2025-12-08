/// <reference types="vite/client" />

// CSS modules type declaration
declare module '*.css' {
  const content: Record<string, string>
  export default content
}
