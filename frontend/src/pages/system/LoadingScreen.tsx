import { Loader } from "../../components/ui";

export function LoadingScreen() {
  return (
    <main className="grid min-h-screen place-items-center px-4">
      <div className="grid justify-items-center gap-5 text-center">
        <Loader />
        <div>
          <p className="text-xl font-black text-[var(--app-text)]">DilpDa</p>
          <p className="text-sm font-medium text-brand-muted">Preparing your experience</p>
        </div>
      </div>
    </main>
  );
}
