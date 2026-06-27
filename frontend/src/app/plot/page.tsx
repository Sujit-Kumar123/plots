import type { Metadata } from "next";
import PlotCanvas from "./_components/plot-canvas";

export const metadata: Metadata = {
  title: "3D Construction Plot",
  description: "Interactive 3D block placement and drawing tool",
};

export default async function PlotPage({
  searchParams,
}: {
  searchParams: Promise<{ sheet?: string }>;
}) {
  const params = await searchParams;
  return <PlotCanvas initialSheetId={params.sheet} />;
}
