# Japanese Vocabulary Importer

A Next.js application that generates Japanese vocabulary lists based on thematic categories using LLM integration.

## Features

- Enter a thematic category (e.g., food, nature, travel) to generate related Japanese vocabulary
- Server-side API integration with LLM (supports Groq or OpenAI)
- Structured JSON output with kanji, romaji, English translations, and parts breakdown
- Copy-to-clipboard functionality with user notification
- Clean, responsive UI

## Project Structure

```
japanese-vocab-importer/
├── app/
│   ├── api/
│   │   └── generate-vocab/
│   │       └── route.ts       # API endpoint for LLM integration
│   ├── page.tsx               # Main page component
│   └── layout.tsx             # Root layout with metadata
├── components/
│   └── VocabImporter.tsx      # Vocabulary importer component
├── types/
│   └── index.ts               # TypeScript type definitions
├── .env.local                 # Environment variables (API keys)
└── package.json
```

## Setup Instructions

### Prerequisites

- Node.js 18.17.0 or later
- API key from Groq or OpenAI (or use the mock version for testing)

### Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd japanese-vocab-importer
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env.local` file in the root directory:
   ```
   # If using Groq API
   GROQ_API_KEY=your_groq_api_key
   
   # If using OpenAI API
   OPENAI_API_KEY=your_openai_api_key
   ```

### Running the Application

Start the development server:
```bash
npm run dev
```

The application will be available at http://localhost:3000.

## API Options

This project provides three implementation options for the vocabulary generation API:

1. **Groq API Integration** - Uses Groq's LLM API for vocabulary generation
2. **OpenAI API Integration** - Uses OpenAI's API (GPT-4 or similar) for vocabulary generation
3. **Mock API** - Returns sample data for testing without requiring any API keys

To switch between implementations, replace the content of `app/api/generate-vocab/route.ts` with the desired version from the provided code examples.

#### OpenAI API Version
```ts
// =============== Make the API call to OpenAI ===============
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
    },
    body: JSON.stringify({
        model: 'gpt-4',
        messages: [
        { role: 'system', content: 'You are a helpful assistant that generates Japanese vocabulary lists in JSON format.' },
        { role: 'user', content: prompt }
        ],
        temperature: 0.7,
        max_tokens: 2000
    })
    });
    
    if (!response.ok) {
    throw new Error(`OpenAI API error: ${response.status}`);
    }
    
    const completion = await response.json();
    // =============== END API call to Groq ===============
```

### Mock API Version for testing
```ts
// /app/api/generate-vocab/route.ts     (The complete code to be replaced)
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { theme } = await request.json();
    
    console.log(`Generating vocabulary for theme: ${theme}`);
    
    // Create mock data based on the theme
    const mockVocabulary = [
      {
        "kanji": "食べ物",
        "romaji": "tabemono",
        "english": "food",
        "parts": [
          { "kanji": "食", "romaji": ["ta", "be"] },
          { "kanji": "物", "romaji": ["mono"] }
        ]
      },
      {
        "kanji": "美味しい",
        "romaji": "oishii",
        "english": "delicious",
        "parts": [
          { "kanji": "美", "romaji": ["o"] },
          { "kanji": "味", "romaji": ["i"] },
          { "kanji": "しい", "romaji": ["shii"] }
        ]
      },
      {
        "kanji": "料理",
        "romaji": "ryouri",
        "english": "cooking",
        "parts": [
          { "kanji": "料", "romaji": ["ryou"] },
          { "kanji": "理", "romaji": ["ri"] }
        ]
      }
    ];
    
    // Add a simulated delay to mimic API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return NextResponse.json({ vocabulary: mockVocabulary });
  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json({ error: 'Failed to process request' }, { status: 500 });
  }
}
```

## Output Format

The generated vocabulary follows this JSON structure:

```json
[
  {
    "kanji": "食べ物",
    "romaji": "tabemono",
    "english": "food",
    "parts": [
      { "kanji": "食", "romaji": ["ta", "be"] },
      { "kanji": "物", "romaji": ["mono"] }
    ]
  },
  ...
]
```

## Browser Compatibility

This application works in all modern browsers. If you encounter React hydration warnings in Chrome, they may be caused by browser extensions that modify the DOM (like Grammarly). These warnings don't affect functionality and can be avoided by using a browser without extensions or using incognito mode.

## License

[MIT License](LICENSE)