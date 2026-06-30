import { FiArrowLeft } from "react-icons/fi";
import { Link } from "react-router-dom";

import { Button, Card } from "../../components/ui";

export function NotFoundPage() {
  return (
    <main className="grid min-h-screen place-items-center px-4 py-10">
      <Card className="w-full max-w-xl p-8 text-center">
        <p className="text-sm font-bold uppercase tracking-[0.3em] text-brand-primary">404</p>
        <h1 className="mt-4 text-4xl font-black text-[var(--app-text)]">Page not found</h1>
        <p className="mx-auto mt-3 max-w-sm text-brand-muted">
          The route you opened is not available in this foundation build.
        </p>
        <Link className="mt-7 inline-flex" to="/">
          <Button icon={<FiArrowLeft />}>Back to foundation</Button>
        </Link>
      </Card>
    </main>
  );
}
