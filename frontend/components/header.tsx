import { Film } from 'lucide-react';

export function Header() {
  return (
    <header className="border-b border-border bg-background">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent">
            <Film className="h-5 w-5 text-accent-foreground" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-foreground">VideoRAG</h1>
            <p className="text-xs text-muted-foreground">AI-powered video analysis</p>
          </div>
        </div>
        <div className="text-right text-sm text-muted-foreground">
          <p>Intelligent video Q&A</p>
        </div>
      </div>
    </header>
  );
}
