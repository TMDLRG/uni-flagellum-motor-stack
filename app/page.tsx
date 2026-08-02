import type { Metadata } from "next";
import { UniFlagellumLab } from "./uni-flagellum-lab";

export const metadata: Metadata = {
  title: "UNI-FLAGELLUM · Living Science Walkthrough",
  description:
    "A source-pinned, CPU-only guided laboratory for observing, reconstructing, calculating, challenging, and reproducing bacterial flagellar-motor science.",
};

export default function Home() {
  return <UniFlagellumLab />;
}
