/**
 * Top header bar with application title and tagline.
 */
export function Header() {
  return (
    <header className="flex items-center gap-3 px-6 py-3 bg-gray-900 border-b border-gray-800 shrink-0">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="28"
        height="28"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="text-orange-500 shrink-0"
        aria-hidden="true"
      >
        <ellipse cx="12" cy="5" rx="9" ry="3" />
        <path d="M3 5V19A9 3 0 0 0 21 19V5" />
        <path d="M3 12A9 3 0 0 0 21 12" />
      </svg>
      <div>
        <h1 className="text-lg font-semibold text-gray-100 leading-tight">
          Data Copilot
        </h1>
        <p className="text-xs text-gray-400 leading-tight">
          Ask questions across your databases, files, and the web
        </p>
      </div>
    </header>
  );
}
