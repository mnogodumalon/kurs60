import re

class TypeScriptGenerator:
    def __init__(self, metadata: dict):
        self.metadata = metadata
        self.apps = metadata["apps"]

    def _to_pascal_case(self, text: str) -> str:
        """Macht aus 'workout_logs' -> 'WorkoutLogs'"""
        # Umlaute ersetzen
        text = text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        # Alles was kein Buchstabe/Zahl ist zu Space, dann Capitalize
        return "".join(word.capitalize() for word in re.sub(r"[^a-zA-Z0-9]", " ", text).split())

    def _map_type(self, control: dict) -> str:
        """Wandelt Living Apps Typen in TypeScript Typen um"""
        ftype = control.get("fulltype", "string")

        if ftype == "number":
            return "number"
        elif ftype == "bool":
            return "boolean"
        elif ftype == "date/date" or ftype == "date/datetimeminute":
            return "string" # API liefert ISO Strings
        elif ftype == "lookup/select" and "lookup_data" in control:
            # Wir generieren einen exakten Union Type: 'option1' | 'option2'
            options = [f"'{k}'" for k in control["lookup_data"].keys()]
            if not options: return "string"
            return " | ".join(options)

        # Fallback für Text, Files, AppLookups (die sind URLs)
        return "string"

    def generate_types(self) -> str:
        """Erzeugt src/types/app.ts mit Smart Comments für App-Lookups"""
        lines = ["// AUTOMATICALLY GENERATED TYPES - DO NOT EDIT", ""]

        # 1. Helper Map aufbauen: App ID -> App Name
        app_id_to_name = {}
        for key, data in self.apps.items():
            # Name bereinigen (PascalCase für Kommentar)
            clean_name = self._to_pascal_case(key)
            app_id_to_name[data["app_id"]] = clean_name

        # 2. Interfaces für jede App generieren
        for app_key, app_data in self.apps.items():
            interface_name = self._to_pascal_case(app_key)

            lines.append(f"export interface {interface_name} {{")
            lines.append("  record_id: string;")
            lines.append("  createdat: string;")
            lines.append("  updatedat: string | null;")
            lines.append("  fields: {")

            # Alle Controls (Felder) durchgehen
            for ctrl_key, ctrl_data in app_data["controls"].items():
                ts_type = self._map_type(ctrl_data)

                # Smart Comment Logic
                comment = ""
                fulltype = ctrl_data.get("fulltype", "")

                if "date" in fulltype:
                    comment = " // Format: YYYY-MM-DD oder ISO String"

                elif fulltype == "applookup/select" and "lookup_app" in ctrl_data:
                    # Versuche herauszufinden, auf welche App das zeigt
                    try:
                        target_id = ctrl_data["lookup_app"].split("/")[-1]
                        target_name = app_id_to_name.get(target_id, "UnknownApp")
                        comment = f" // applookup -> URL zu '{target_name}' Record"
                    except:
                        comment = " // applookup -> URL zum Record"

                # Zeile hinzufügen (immer optional mit ?)
                lines.append(f"    {ctrl_key}?: {ts_type};{comment}")

            lines.append("  };")
            lines.append("}")
            lines.append("")

        # 3. App IDs Konstante exportieren
        lines.append("export const APP_IDS = {")
        for app_key, app_data in self.apps.items():
            # Konstanten-Name: WORKOUT_LOGS statt WorkoutLogs
            const_name = app_key.upper().replace("-", "_").replace("&", "").replace(" ", "_")
            # Doppelte Underscores bereinigen
            const_name = re.sub(r"_+", "_", const_name)

            lines.append(f"  {const_name}: '{app_data['app_id']}',")
        lines.append("} as const;")
        lines.append("")

        # 4. Helper Types für Create-Operationen (Omit record_id etc.)
        lines.append("// Helper Types for creating new records")
        for app_key in self.apps.keys():
            interface_name = self._to_pascal_case(app_key)
            lines.append(f"export type Create{interface_name} = {interface_name}['fields'];")

        return "\n".join(lines)

    def generate_service(self) -> str:
        """Erzeugt src/services/livingAppsService.ts (Full Featured)"""

        # Header & Helper Functions (Statisch)
        lines = [
            "// AUTOMATICALLY GENERATED SERVICE",
            "import { APP_IDS } from '@/types/app';",
            # Dynamische Imports der Typen
            f"import type {{ {', '.join([self._to_pascal_case(k) for k in self.apps.keys()])} }} from '@/types/app';",
            "",
            "// Base Configuration",
            "const API_BASE_URL = 'https://my.living-apps.de/rest';",
            "",
            "// --- HELPER FUNCTIONS ---",
            "export function extractRecordId(url: string | null | undefined): string | null {",
            "  if (!url) return null;",
            "  // Extrahiere die letzten 24 Hex-Zeichen mit Regex",
            "  const match = url.match(/([a-f0-9]{24})$/i);",
            "  return match ? match[1] : null;",
            "}",
            "",
            "export function createRecordUrl(appId: string, recordId: string): string {",
            "  return `https://my.living-apps.de/rest/apps/${appId}/records/${recordId}`;",
            "}",
            "",
            "async function callApi(method: string, endpoint: string, data?: any) {",
            "  const response = await fetch(`${API_BASE_URL}${endpoint}`, {",
            "    method,",
            "    headers: { 'Content-Type': 'application/json' },",
            "    credentials: 'include',  // Nutze Session Cookies für Auth",
            "    body: data ? JSON.stringify(data) : undefined",
            "  });",
            "  if (!response.ok) throw new Error(await response.text());",
            "  // DELETE returns often empty body or simple status",
            "  if (method === 'DELETE') return true;",
            "  return response.json();",
            "}",
            "",
            "export class LivingAppsService {",
        ]

        # Methoden generieren
        for app_key, app_data in self.apps.items():
            class_name = self._to_pascal_case(app_key) # Plural Interface Name (z.B. Workouts)
            const_name = app_key.upper().replace("-", "_").replace("&", "").replace(" ", "_")
            const_name = re.sub(r"_+", "_", const_name)

            # Singular Name für Methoden (z.B. getWorkout statt getWorkoutsEntry)
            # Einfache Heuristik: Wenn es auf 's' endet, weg damit. Sonst 'Entry' anhängen.
            singular_name = class_name[:-1] if class_name.endswith("s") else f"{class_name}Entry"

            lines.append(f"  // --- {app_key.upper()} ---")

            # GET ALL
            lines.append(f"  static async get{class_name}(): Promise<{class_name}[]> {{")
            lines.append(f"    const data = await callApi('GET', `/apps/${{APP_IDS.{const_name}}}/records`);")
            lines.append("    return Object.entries(data).map(([id, rec]: [string, any]) => ({")
            lines.append("      record_id: id, ...rec")
            lines.append("    }));")
            lines.append("  }")

            # GET ONE
            lines.append(f"  static async get{singular_name}(id: string): Promise<{class_name} | undefined> {{")
            lines.append(f"    const data = await callApi('GET', `/apps/${{APP_IDS.{const_name}}}/records/${{id}}`);")
            lines.append("    return { record_id: data.id, ...data };")
            lines.append("  }")

            # CREATE
            lines.append(f"  static async create{singular_name}(fields: {class_name}['fields']) {{")
            lines.append(f"    return callApi('POST', `/apps/${{APP_IDS.{const_name}}}/records`, {{ fields }});")
            lines.append("  }")

            # UPDATE
            lines.append(f"  static async update{singular_name}(id: string, fields: Partial<{class_name}['fields']>) {{")
            lines.append(f"    return callApi('PATCH', `/apps/${{APP_IDS.{const_name}}}/records/${{id}}`, {{ fields }});")
            lines.append("  }")

            # DELETE
            lines.append(f"  static async delete{singular_name}(id: string) {{")
            lines.append(f"    return callApi('DELETE', `/apps/${{APP_IDS.{const_name}}}/records/${{id}}`);")
            lines.append("  }")

            lines.append("")

        lines.append("}")
        return "\n".join(lines)