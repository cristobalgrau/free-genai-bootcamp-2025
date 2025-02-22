
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Link } from "react-router-dom";

const Groups = () => {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Word Groups</h1>
        <p className="text-muted-foreground">
          Manage your vocabulary groups.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Core Verbs</CardTitle>
          </CardHeader>
          <CardContent>
            <Link 
              to="/groups/1" 
              className="text-sm text-muted-foreground hover:text-foreground"
            >
              View 150 words
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Groups;
