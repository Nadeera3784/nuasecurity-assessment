import { Globe, Smartphone } from "lucide-react";

export const ASSET_TYPES = [
  { value: "mobile", label: "Mobile App", icon: Smartphone },
  { value: "web", label: "Web", icon: Globe },
] as const;
