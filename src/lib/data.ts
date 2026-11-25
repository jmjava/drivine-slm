import conceptsData from "../../data/concepts.json";
import instructData from "../../data/drivine_instruct.json";
import profilesData from "../../data/amd_profiles.json";

export type Concept = {
  id: string;
  title: string;
  category: string;
  summary: string;
  detail: string;
  related: string[];
};

export type InstructRow = {
  id: string;
  topic: string;
  instruction: string;
  response: string;
  summary?: string;
};

export type AmdProfile = {
  id: string;
  name: string;
  chip: string;
  gpu: string;
  gfx: string;
  unifiedMemoryGb: number;
  recommendedVramGb: number;
  torchIndex: string;
  torchPackage: string;
  notes: string[];
  defaultTrain: {
    model: string;
    method: string;
    loraR: number;
    loraAlpha: number;
    maxSeqLen: number;
    batchSize: number;
    gradAccum: number;
    lr: number;
    maxSteps: number;
  };
};

export function getConcepts(): Concept[] {
  return conceptsData as Concept[];
}

export function getInstruct(): InstructRow[] {
  return instructData as InstructRow[];
}

export function getProfiles(): AmdProfile[] {
  return profilesData as AmdProfile[];
}
