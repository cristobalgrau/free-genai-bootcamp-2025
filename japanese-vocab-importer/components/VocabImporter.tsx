'use client';

import { useState, useRef } from 'react';
import { VocabItem } from '../types';

export default function VocabImporter() {
  const [theme, setTheme] = useState('');
  const [vocabulary, setVocabulary] = useState<VocabItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const textAreaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!theme.trim()) {
      setError('Please enter a theme');
      return;
    }
    
    setLoading(true);
    setError('');
    setCopied(false);
    
    try {
      const response = await fetch('/api/generate-vocab', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ theme }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate vocabulary');
      }
      
      setVocabulary(data.vocabulary);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      setVocabulary([]);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (textAreaRef.current) {
      textAreaRef.current.select();
      navigator.clipboard.writeText(textAreaRef.current.value);
      setCopied(true);
      
      // Alert that disappears after 3 seconds
      setTimeout(() => {
        setCopied(false);
      }, 3000);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h1 className="text-2xl font-bold mb-6">Japanese Vocabulary Importer</h1>
      
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="mb-4">
          <label htmlFor="theme" className="block text-sm font-medium text-gray-700 mb-1">
            Enter a thematic category:
          </label>
          <input
            id="theme"
            type="text"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., food, nature, technology, emotions"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-blue-300"
        >
          {loading ? 'Generating...' : 'Generate Vocabulary'}
        </button>
      </form>
      
      {error && (
        <div className="mb-6 p-4 bg-red-100 text-red-700 rounded-md">
          {error}
        </div>
      )}
      
      {vocabulary.length > 0 && (
        <div className="mt-6">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-xl font-semibold">Generated Vocabulary</h2>
            <button
              onClick={copyToClipboard}
              className="px-3 py-1 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Copy to Clipboard
            </button>
          </div>
          
          {copied && (
            <div className="mb-3 p-2 bg-green-100 text-green-700 rounded-md text-center">
              Copied to clipboard!
            </div>
          )}
          
          <textarea
            ref={textAreaRef}
            value={JSON.stringify(vocabulary, null, 2)}
            readOnly
            className="w-full h-64 p-4 bg-gray-50 border border-gray-300 rounded-md font-mono text-sm overflow-auto"
          />
        </div>
      )}
    </div>
  );
}
