import { NextResponse } from "next/server";
import { getInstruct } from "@/lib/data";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const q = (searchParams.get("q") ?? "").trim().toLowerCase();
  const topic = (searchParams.get("topic") ?? "").trim().toLowerCase();
  const rows = getInstruct();
  const filtered = rows.filter((row) => {
    if (topic && row.topic.toLowerCase() !== topic) return false;
    if (!q) return true;
    const hay = `${row.instruction} ${row.response} ${row.topic}`.toLowerCase();
    return hay.includes(q);
  });
  return NextResponse.json({
    total: rows.length,
    count: filtered.length,
    rows: filtered,
    sample: true,
  });
}
