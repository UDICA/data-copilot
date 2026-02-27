import { useState, useCallback, type FormEvent } from 'react';

/**
 * Simple form for adding a new data source connection.
 *
 * Currently placeholder functionality -- submitting logs the values
 * to the console. In production this would POST to /api/sources.
 */
export function ConnectionForm() {
  const [name, setName] = useState('');
  const [connectionString, setConnectionString] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();
      if (!name.trim() || !connectionString.trim()) return;

      // Placeholder: in production, POST to /api/sources
      console.info('New source connection:', { name, connectionString });
      setSubmitted(true);
      setName('');
      setConnectionString('');
      setTimeout(() => setSubmitted(false), 3000);
    },
    [name, connectionString]
  );

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <h3 className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
        Add Connection
      </h3>
      <div>
        <label htmlFor="source-name" className="block text-xs font-medium text-gray-600 mb-1">
          Name
        </label>
        <input
          id="source-name"
          type="text"
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="My Database"
          className="w-full rounded-md border border-gray-300 px-2.5 py-1.5 text-sm text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
        />
      </div>
      <div>
        <label htmlFor="connection-string" className="block text-xs font-medium text-gray-600 mb-1">
          Connection String
        </label>
        <input
          id="connection-string"
          type="text"
          value={connectionString}
          onChange={e => setConnectionString(e.target.value)}
          placeholder="postgresql://user:pass@host/db"
          className="w-full rounded-md border border-gray-300 px-2.5 py-1.5 text-sm text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
        />
      </div>
      <button
        type="submit"
        disabled={!name.trim() || !connectionString.trim()}
        className="w-full rounded-md bg-gray-800 px-3 py-1.5 text-xs font-medium text-white hover:bg-gray-700 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 focus:outline-none disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        Connect
      </button>
      {submitted && (
        <p className="text-xs text-green-600 text-center">
          Connection request submitted
        </p>
      )}
    </form>
  );
}
