export interface VocabPart {
  kanji: string;
  romaji: string[];
}

export interface VocabItem {
  kanji: string;
  romaji: string;
  english: string;
  parts: VocabPart[];
}
