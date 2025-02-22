
import { useState } from "react";
import { WordTable } from "@/components/shared/WordTable";

const mockWords = [
  {
    id: "1",
    japanese: "こんにちは",
    romaji: "konnichiwa",
    english: "hello",
    correctCount: 10,
    wrongCount: 2,
  },
  // Add more mock data as needed
];

const Words = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortColumn, setSortColumn] = useState<string>();
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const handleSort = (column: string) => {
    setSortColumn(column);
    setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Words</h1>
        <p className="text-muted-foreground">
          Browse and manage your Japanese vocabulary.
        </p>
      </div>

      <WordTable
        words={mockWords}
        totalPages={1}
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        onSort={handleSort}
        sortColumn={sortColumn}
        sortDirection={sortDirection}
      />
    </div>
  );
};

export default Words;
