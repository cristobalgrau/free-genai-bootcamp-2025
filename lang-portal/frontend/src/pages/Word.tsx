
import { useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Volume2 } from "lucide-react";

const Word = () => {
  const { id } = useParams();

  // Sample word data
  const word = {
    id,
    japanese: "食べる",
    romaji: "taberu",
    english: "to eat",
    type: "Verb (Group 2)",
    tags: ["Common", "Daily Life", "Actions"],
    notes: "This is an ichidan verb, meaning it follows a regular conjugation pattern.",
    examples: [
      {
        japanese: "私はりんごを食べる",
        romaji: "watashi wa ringo wo taberu",
        english: "I eat an apple",
      },
      {
        japanese: "朝ごはんを食べました",
        romaji: "asagohan wo tabemashita",
        english: "I ate breakfast",
      },
    ],
    stats: {
      correctCount: 45,
      wrongCount: 5,
      lastReviewed: "2024-02-20",
      successRate: "90%",
    },
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight japanese-text">
          {word.japanese}
        </h1>
        <p className="text-muted-foreground">
          {word.romaji} - {word.english}
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Word Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-2">
              <span className="text-2xl japanese-text">{word.japanese}</span>
              <Button variant="ghost" size="sm">
                <Volume2 className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="space-y-2">
              <p>
                <span className="font-medium">Romaji:</span> {word.romaji}
              </p>
              <p>
                <span className="font-medium">English:</span> {word.english}
              </p>
              <p>
                <span className="font-medium">Type:</span> {word.type}
              </p>
              <div className="flex flex-wrap gap-2 mt-2">
                {word.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 bg-secondary text-secondary-foreground rounded-md text-sm"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <p className="font-medium mb-2">Notes:</p>
              <p className="text-muted-foreground">{word.notes}</p>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Examples</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {word.examples.map((example, index) => (
                <div key={index} className="space-y-1 pb-4 last:pb-0 border-b last:border-0">
                  <p className="japanese-text">{example.japanese}</p>
                  <p className="text-sm">{example.romaji}</p>
                  <p className="text-sm text-muted-foreground">{example.english}</p>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Study Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Correct Answers:</span>
                  <span className="text-japanese-success">{word.stats.correctCount}</span>
                </div>
                <div className="flex justify-between">
                  <span>Wrong Answers:</span>
                  <span className="text-japanese-error">{word.stats.wrongCount}</span>
                </div>
                <div className="flex justify-between">
                  <span>Success Rate:</span>
                  <span>{word.stats.successRate}</span>
                </div>
                <div className="flex justify-between">
                  <span>Last Reviewed:</span>
                  <span>{word.stats.lastReviewed}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Word;
