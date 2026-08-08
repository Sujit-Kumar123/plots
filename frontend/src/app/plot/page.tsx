import type { Metadata } from "next";
import PlotCanvas from "./_components/plot-canvas";
import { apiListCatalogItems } from "@/lib/services/plot-catalog";

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
  // Not awaited — passed down as a Promise so <CatalogPanel> can suspend on it independently.
  const catalogPromise = apiListCatalogItems();
  return <PlotCanvas initialSheetId={params.sheet} catalogPromise={catalogPromise} />;
}
