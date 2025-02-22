
import { useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const StudyActivity = () => {
  const { id } = useParams();

  // Sample activity data
  const activity = {
    id,
    title: "Adventure MUD",
    description: "Text-based adventure game for learning Japanese",
    thumbnail: "/placeholder.svg",
    sessions: [
      {
        id: "1",
        groupName: "Core Verbs",
        groupId: "1",
        startTime: "2024-02-20 09:30 AM",
        endTime: "2024-02-20 10:15 AM",
        reviewItems: 47,
      },
      {
        id: "2",
        groupName: "Basic Adjectives",
        groupId: "2",
        startTime: "2024-02-19 02:00 PM",
        endTime: "2024-02-19 02:45 PM",
        reviewItems: 35,
      },
      {
        id: "3",
        groupName: "Core Verbs",
        groupId: "1",
        startTime: "2024-02-18 11:15 AM",
        endTime: "2024-02-18 12:00 PM",
        reviewItems: 52,
      },
    ],
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{activity.title}</h1>
        <p className="text-muted-foreground">{activity.description}</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Activity Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="aspect-video bg-muted rounded-lg overflow-hidden">
              <img
                src={activity.thumbnail}
                alt={activity.title}
                className="w-full h-full object-cover"
              />
            </div>
            <Button asChild className="w-full">
              <a href={`http://localhost:8081?group_id=${activity.id}`} target="_blank">
                Launch Activity
              </a>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Sessions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {activity.sessions.map((session) => (
                <div key={session.id} className="border-b pb-4 last:border-0">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-medium hover:text-japanese-primary">
                        {session.groupName}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {session.reviewItems} words reviewed
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm">{session.startTime}</p>
                      <p className="text-sm text-muted-foreground">
                        to {session.endTime}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default StudyActivity;
