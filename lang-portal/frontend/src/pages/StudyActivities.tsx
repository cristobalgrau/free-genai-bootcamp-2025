
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

const StudyActivities = () => {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Study Activities</h1>
        <p className="text-muted-foreground">
          Choose an activity to start learning.
        </p>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Adventure MUD</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              Learn Japanese through text-based adventure games.
            </p>
            <div className="flex space-x-2">
              <Button asChild>
                <a href="http://localhost:8081?group_id=1" target="_blank">
                  Launch
                </a>
              </Button>
              <Button variant="outline" asChild>
                <Link to="/study-activities/1">View</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default StudyActivities;
