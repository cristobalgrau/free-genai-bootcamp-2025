
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Link } from "react-router-dom";

const Sessions = () => {
  // Sample sessions data
  const sessions = [
    {
      id: "1",
      activityName: "Adventure MUD",
      activityId: "1",
      groupName: "Core Verbs",
      groupId: "1",
      startTime: "2024-02-20 09:30 AM",
      endTime: "2024-02-20 10:15 AM",
      duration: "45 minutes",
      reviewItems: 47,
      correctCount: 42,
      wrongCount: 5,
    },
    {
      id: "2",
      activityName: "Typing Tutor",
      activityId: "2",
      groupName: "Basic Adjectives",
      groupId: "2",
      startTime: "2024-02-19 02:00 PM",
      endTime: "2024-02-19 02:45 PM",
      duration: "45 minutes",
      reviewItems: 35,
      correctCount: 30,
      wrongCount: 5,
    },
    {
      id: "3",
      activityName: "Adventure MUD",
      activityId: "1",
      groupName: "Core Verbs",
      groupId: "1",
      startTime: "2024-02-18 11:15 AM",
      endTime: "2024-02-18 12:00 PM",
      duration: "45 minutes",
      reviewItems: 52,
      correctCount: 45,
      wrongCount: 7,
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Study Sessions</h1>
        <p className="text-muted-foreground">
          Review your learning history.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Sessions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {sessions.map((session) => (
              <div
                key={session.id}
                className="border-b pb-6 last:pb-0 last:border-0"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <Link
                      to={`/study-activities/${session.activityId}`}
                      className="text-lg font-medium hover:text-japanese-primary"
                    >
                      {session.activityName}
                    </Link>
                    <Link
                      to={`/groups/${session.groupId}`}
                      className="block text-sm text-muted-foreground hover:text-foreground"
                    >
                      {session.groupName}
                    </Link>
                  </div>
                  <div className="text-right">
                    <p className="text-sm">{session.startTime}</p>
                    <p className="text-sm text-muted-foreground">
                      Duration: {session.duration}
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Words Reviewed</p>
                    <p className="font-medium">{session.reviewItems}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Correct</p>
                    <p className="font-medium text-japanese-success">
                      {session.correctCount}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Wrong</p>
                    <p className="font-medium text-japanese-error">
                      {session.wrongCount}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Sessions;
