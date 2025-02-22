
import { useParams } from "react-router-dom";
import { WordTable } from "@/components/shared/WordTable";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const Group = () => {
  const { id } = useParams();
  const [currentPage, setCurrentPage] = useState(1);
  const [sortColumn, setSortColumn] = useState<string>();
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  // Sample group data
  const group = {
    id,
    name: "Core Verbs",
    description: "Essential verbs for daily conversation",
    totalWords: 150,
    lastStudied: "2024-02-20",
    successRate: "85%",
    words: [
      {
        id: "1",
        japanese: "食べる",
        romaji: "taberu",
        english: "to eat",
        correctCount: 45,
        wrongCount: 5,
      },
      {
        id: "2",
        japanese: "飲む",
        romaji: "nomu",
        english: "to drink",
        correctCount: 38,
        wrongCount: 3,
      },
      {
        id: "3",
        japanese: "見る",
        romaji: "miru",
        english: "to see",
        correctCount: 42,
        wrongCount: 4,
      },
      {
        id: "4",
        japanese: "聞く",
        romaji: "kiku",
        english: "to listen/hear",
        correctCount: 35,
        wrongCount: 7,
      },
    ],
  };

  const handleSort = (column: string) => {
    setSortColumn(column);
    setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{group.name}</h1>
        <p className="text-muted-foreground">{group.description}</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Total Words</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{group.totalWords}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Success Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-japanese-success">
              {group.successRate}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Last Studied</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{group.lastStudied}</p>
          </CardContent>
        </Card>
      </div>

      <WordTable
        words={group.words}
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

export default Group;
