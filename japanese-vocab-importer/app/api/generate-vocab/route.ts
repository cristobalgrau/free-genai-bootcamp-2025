import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { theme } = await request.json();
    
    // Create the prompt for vocabulary generation
    const prompt = `Generate a list of Japanese vocabulary words related to the theme: "${theme}".
    Please return ONLY a valid JSON array without any additional text or explanation.
    Each word should include kanji, romaji, English translation, and parts breakdown.
    Format example:
    [
      {
        "kanji": "いい", 
        "romaji": "ii", 
        "english": "good", 
        "parts": [
          { "kanji": "い", "romaji": ["i"] }, 
          { "kanji": "い", "romaji": ["i"] }
        ]
      },
      {
        "kanji": "良い", 
        "romaji": "yoi", 
        "english": "good", 
        "parts": [
          { "kanji": "良", "romaji": ["yo"] }, 
          { "kanji": "い", "romaji": ["i"] }
        ]
      }
    ]`;
    
    // =============== Make the API call to Groq using fetch ===============
    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.GROQ_API_KEY}`
      },
      body: JSON.stringify({
        model: 'llama3-70b-8192',
        messages: [
          { role: 'system', content: 'You are a helpful assistant that generates Japanese vocabulary lists in JSON format.' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.7,
        max_tokens: 2000
      })
    });
    
    if (!response.ok) {
      throw new Error(`Groq API error: ${response.status}`);
    }
    
    const completion = await response.json();
    // =============== END API call to Groq ===============
    
    // Extract and parse the JSON response
    const responseContent = completion.choices[0].message.content || '[]';
    
    // Try to parse the JSON and handle potential errors
    let vocabularyList;
    try {
      vocabularyList = JSON.parse(responseContent);
      
      // Validate the response structure
      if (!Array.isArray(vocabularyList)) {
        throw new Error('Response is not an array');
      }
      
      // Basic validation of each item
      vocabularyList.forEach((item: any) => {
        if (!item.kanji || !item.romaji || !item.english || !Array.isArray(item.parts)) {
          throw new Error('Invalid item structure in response');
        }
      });
      
    } catch (error) {
      console.error('Failed to parse LLM response:', error);
      return NextResponse.json({ error: 'Failed to generate vocabulary list' }, { status: 500 });
    }
    
    return NextResponse.json({ vocabulary: vocabularyList });
  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json({ error: 'Failed to process request' }, { status: 500 });
  }
}
