/// <reference types="vite/client" />

// CSS module declarations
declare module "*.css" {
  const content: string;
  export default content;
}
