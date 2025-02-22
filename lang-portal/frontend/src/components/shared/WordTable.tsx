
import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Volume2, ArrowUp, ArrowDown, ChevronLeft, ChevronRight } from "lucide-react";

interface WordData {
  id: string;
  japanese: string;
  romaji: string;
  english: string;
  correctCount: number;
  wrongCount: number;
  audioUrl?: string;
}

interface WordTableProps {
  words: WordData[];
  totalPages: number;
  currentPage: number;
  onPageChange: (page: number) => void;
  onSort: (column: string) => void;
  sortColumn?: string;
  sortDirection?: 'asc' | 'desc';
}

export const WordTable = ({
  words,
  totalPages,
  currentPage,
  onPageChange,
  onSort,
  sortColumn,
  sortDirection,
}: WordTableProps) => {
  const playAudio = (url: string) => {
    const audio = new Audio(url);
    audio.play().catch(console.error);
  };

  const getSortIcon = (column: string) => {
    if (sortColumn !== column) return null;
    return sortDirection === 'asc' ? <ArrowDown className="h-4 w-4" /> : <ArrowUp className="h-4 w-4" />;
  };

  return (
    <div className="space-y-4">
      <div className="rounded-lg border bg-card">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              {['Japanese', 'Romaji', 'English', '# Correct', '# Wrong'].map((header) => (
                <th
                  key={header}
                  className="px-4 py-2 text-left font-medium text-muted-foreground"
                  onClick={() => onSort(header.toLowerCase())}
                >
                  <div className="flex items-center space-x-2 cursor-pointer hover:text-foreground">
                    <span>{header}</span>
                    {getSortIcon(header.toLowerCase())}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {words.map((word) => (
              <tr key={word.id} className="border-b last:border-0">
                <td className="px-4 py-2">
                  <div className="flex items-center space-x-2">
                    <Link
                      to={`/words/${word.id}`}
                      className="text-lg font-medium hover:text-japanese-primary transition-colors japanese-text"
                    >
                      {word.japanese}
                    </Link>
                    {word.audioUrl && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => playAudio(word.audioUrl!)}
                      >
                        <Volume2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </td>
                <td className="px-4 py-2">{word.romaji}</td>
                <td className="px-4 py-2">{word.english}</td>
                <td className="px-4 py-2 text-japanese-success">{word.correctCount}</td>
                <td className="px-4 py-2 text-japanese-error">{word.wrongCount}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-center space-x-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <span className="text-sm text-muted-foreground">
          Page{" "}
          <strong className="text-foreground">{currentPage}</strong> of{" "}
          {totalPages}
        </span>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};
