import { NextResponse } from "next/server";
import { getProfiles } from "@/lib/data";

export async function GET() {
  return NextResponse.json({ profiles: getProfiles(), sample: true });
}
