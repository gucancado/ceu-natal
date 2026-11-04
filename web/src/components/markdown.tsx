import ReactMarkdown, { type Components } from "react-markdown";

// Texto jurídico em Markdown, sem HTML cru. Estilo próprio, sem plugin typography.
const componentes: Components = {
  h1: ({ children }) => (
    <h1 className="font-display text-4xl font-medium leading-[1.15] tracking-tight md:text-5xl">{children}</h1>
  ),
  h2: ({ children }) => <h2 className="mt-10 font-display text-2xl font-medium leading-[1.25]">{children}</h2>,
  h3: ({ children }) => <h3 className="mt-8 font-display text-xl font-medium">{children}</h3>,
  p: ({ children }) => <p className="mt-4">{children}</p>,
  ul: ({ children }) => <ul className="mt-4 list-disc space-y-2 pl-6">{children}</ul>,
  ol: ({ children }) => <ol className="mt-4 list-decimal space-y-2 pl-6">{children}</ol>,
  a: ({ href, children }) => (
    <a href={href} className="text-honey underline underline-offset-4 [overflow-wrap:anywhere]">
      {children}
    </a>
  ),
  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
  code: ({ children }) => <code className="font-mono text-[0.9em]">{children}</code>,
};

export function Markdown({ texto }: { texto: string }) {
  return (
    <div className="max-w-[68ch] [overflow-wrap:anywhere]">
      <ReactMarkdown components={componentes}>{texto}</ReactMarkdown>
    </div>
  );
}
