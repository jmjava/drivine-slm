import { NextResponse } from "next/server";
import { getConcepts } from "@/lib/data";

export async function GET() {
  return NextResponse.json({ concepts: getConcepts(), sample: true });
}
