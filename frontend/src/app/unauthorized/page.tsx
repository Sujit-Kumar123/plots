import Link from "next/link";
import { ShieldX } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ThemeToggle } from "@/components/theme-toggle";

export default function Unauthorized() {
  return (
    <main className="relative flex flex-1 flex-col items-center justify-center px-4">
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>

      <Card className="w-full max-w-md text-center">
        <CardHeader className="pb-2">
          <div className="flex justify-center mb-4">
            <span className="flex size-16 items-center justify-center rounded-full bg-destructive/10">
              <ShieldX className="size-8 text-destructive" />
            </span>
          </div>
          <div className="flex justify-center mb-2">
            <Badge variant="destructive" className="text-xs px-3 py-0.5">
              Error 403
            </Badge>
          </div>
          <CardTitle className="text-2xl font-bold">Access Denied</CardTitle>
          <CardDescription className="text-sm leading-relaxed">
            You don&apos;t have permission to view this page. Contact your
            administrator if you think this is a mistake.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <Separator />
        </CardContent>

        <CardFooter className="flex justify-center gap-3 border-none bg-transparent">
          <Button asChild>
            <Link href="/dashboard">Go to Dashboard</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/login">Switch Account</Link>
          </Button>
        </CardFooter>
      </Card>
    </main>
  );
}
