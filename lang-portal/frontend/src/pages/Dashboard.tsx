
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const Dashboard = () => {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back! Here's an overview of your progress.
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Words</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2,345</div>
            <p className="text-xs text-muted-foreground">
              +180 from last week
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">89.3%</div>
            <p className="text-xs text-muted-foreground">
              +2.4% from last week
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Study Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24.3h</div>
            <p className="text-xs text-muted-foreground">
              +5.2h from last week
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Word Groups</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">
              +2 new groups
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Last Study Session</CardTitle>
            <CardDescription>
              Your most recent learning activity
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <p className="text-sm font-medium">Activity</p>
                <p className="text-sm text-muted-foreground">
                  Adventure MUD - Core Verbs
                </p>
              </div>
              <div className="space-y-2">
                <p className="text-sm font-medium">Duration</p>
                <p className="text-sm text-muted-foreground">45 minutes</p>
              </div>
              <div className="space-y-2">
                <p className="text-sm font-medium">Performance</p>
                <p className="text-sm text-muted-foreground">
                  42 correct • 5 incorrect
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Stats</CardTitle>
            <CardDescription>Your learning trajectory</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <p className="text-sm font-medium">Weekly Goal</p>
                <div className="h-4 w-full rounded-full bg-secondary">
                  <div
                    className="h-4 rounded-full bg-japanese-primary"
                    style={{ width: "75%" }}
                  />
                </div>
                <p className="text-xs text-muted-foreground">
                  75% complete - 3 days remaining
                </p>
              </div>
              
              <div className="space-y-2">
                <p className="text-sm font-medium">Streak</p>
                <p className="text-2xl font-bold text-japanese-success">
                  🔥 7 days
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
