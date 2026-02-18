import re


class ReactComponentGenerator:
    """
    Generates React components with React Router for CRUD scaffold pages.
    
    Given app metadata (same format as TypeScriptGenerator), generates:
    - src/App.tsx — BrowserRouter with all routes
    - src/components/Layout.tsx — Dark sidebar navigation + Outlet (semantic tokens)
    - src/components/PageShell.tsx — Consistent page header wrapper
    - src/pages/DashboardOverview.tsx — Placeholder overview page with KPI cards
    - src/components/ConfirmDialog.tsx — Generic delete confirmation
    - src/components/StatCard.tsx — Reusable KPI card
    - src/pages/{Entity}Page.tsx — Full CRUD page per scaffolded entity
    - src/components/dialogs/{Entity}Dialog.tsx — Create/edit dialog per scaffolded entity
    - src/pages/{Entity}Page.tsx — Placeholder page for non-scaffolded entities
    
    Naming conventions MUST match TypeScriptGenerator exactly so imports work.
    Auto-detects language (DE/EN) from entity metadata for all UI text.
    """

    ICON_MAP = {
        # People
        "user": "Users", "member": "Users", "employee": "Users",
        "team": "Users", "person": "Users", "customer": "Users",
        "client": "Users", "contact": "Users", "staff": "Users",
        "participant": "Users", "teilnehmer": "Users",
        "mitarbeiter": "Users", "kunde": "Users", "personal": "Users",
        # Education
        "instructor": "GraduationCap", "teacher": "GraduationCap",
        "dozent": "GraduationCap", "trainer": "GraduationCap",
        "course": "BookOpen", "class": "BookOpen", "lesson": "BookOpen",
        "kurs": "BookOpen", "schulung": "BookOpen",
        # Places
        "room": "DoorOpen", "raum": "DoorOpen",
        "location": "MapPin", "standort": "MapPin", "ort": "MapPin",
        "building": "Building2", "gebaeude": "Building2",
        # Work
        "project": "FolderKanban", "projekt": "FolderKanban",
        "task": "CheckSquare", "aufgabe": "CheckSquare",
        "shift": "Clock", "schicht": "Clock",
        "schedule": "CalendarDays", "termin": "CalendarDays",
        "event": "Calendar", "veranstaltung": "Calendar",
        # Commerce
        "product": "Package", "produkt": "Package",
        "item": "Package", "artikel": "Package",
        "inventory": "Boxes", "lager": "Boxes", "bestand": "Boxes",
        "order": "ShoppingCart", "bestellung": "ShoppingCart",
        "invoice": "Receipt", "rechnung": "Receipt",
        # Organization
        "category": "Tag", "kategorie": "Tag",
        "label": "Tags", "tag": "Tags", "type": "Tag", "typ": "Tag",
        "department": "Building", "abteilung": "Building",
        # Equipment / Vehicles
        "vehicle": "Car", "fahrzeug": "Car",
        "equipment": "Wrench", "geraet": "Wrench",
        # Registration / Booking
        "registration": "ClipboardList", "anmeldung": "ClipboardList",
        "booking": "CalendarCheck", "buchung": "CalendarCheck",
    }

    UI_TEXTS = {
        'de': {
            'overview': 'Übersicht',
            'navigation': 'Navigation',
            'cancel': 'Abbrechen',
            'delete': 'Löschen',
            'save': 'Speichern',
            'saving': 'Speichern...',
            'create': 'Erstellen',
            'search': 'Suchen...',
            'actions': 'Aktionen',
            'no_results': 'Keine Ergebnisse gefunden.',
            'no_data_yet': 'Noch keine {entity}. Jetzt hinzufügen!',
            'select_placeholder': 'Auswählen...',
            'confirm_delete_desc': 'Soll dieser Eintrag wirklich gelöscht werden? Diese Aktion kann nicht rückgängig gemacht werden.',
            'add': 'Hinzufügen',
            'edit_entity': '{entity} bearbeiten',
            'new_entity': '{entity} hinzufügen',
            'delete_entity': '{entity} löschen',
            'yes': 'Ja',
            'no': 'Nein',
            'search_entity': '{entity} suchen...',
            'in_system': '{entity} im System',
            'welcome': 'Willkommen',
            'overview_subtitle': 'Hier ist eine Übersicht Ihrer Daten.',
            'management': 'Verwaltung',
            'dashboard': 'Dashboard',
            'date_format': 'dd.MM.yyyy',
        },
        'en': {
            'overview': 'Overview',
            'navigation': 'Navigation',
            'cancel': 'Cancel',
            'delete': 'Delete',
            'save': 'Save',
            'saving': 'Saving...',
            'create': 'Create',
            'search': 'Search...',
            'actions': 'Actions',
            'no_results': 'No results found.',
            'no_data_yet': 'No {entity} yet. Add one!',
            'select_placeholder': 'Select...',
            'confirm_delete_desc': 'Are you sure? This action cannot be undone.',
            'add': 'Add',
            'edit_entity': 'Edit {entity}',
            'new_entity': 'New {entity}',
            'delete_entity': 'Delete {entity}',
            'yes': 'Yes',
            'no': 'No',
            'search_entity': 'Search {entity}...',
            'in_system': '{entity} in the system',
            'welcome': 'Welcome back',
            'overview_subtitle': "Here's an overview of your data.",
            'management': 'Management',
            'dashboard': 'Dashboard',
            'date_format': 'MMM d, yyyy',
        }
    }

    def __init__(self, metadata: dict, crud_scaffolds: list):
        self.metadata = metadata
        self.apps = metadata.get("apps", {})
        self.crud_scaffolds = [s for s in crud_scaffolds if s in self.apps]
        self.app_id_to_identifier = {
            data["app_id"]: key for key, data in self.apps.items()
        }
        self.lang = self._detect_language()

    # ================================================================
    # Language detection + localization
    # ================================================================

    def _detect_language(self) -> str:
        """Detect UI language from entity names and labels."""
        german_chars = set('äöüß')
        german_words = {
            'und', 'der', 'die', 'das', 'für', 'mit', 'von', 'zur', 'zum',
            'aus', 'bei', 'ein', 'eine', 'name', 'datum', 'preis', 'nummer',
            'telefon', 'adresse', 'strasse', 'stadt', 'raum', 'gebaeude',
            'beschreibung', 'bezeichnung', 'bemerkung', 'anmerkung',
        }

        text_parts = []
        for data in self.apps.values():
            text_parts.append(data.get('name', ''))
            for ctrl in data.get('controls', {}).values():
                text_parts.append(ctrl.get('label', ''))

        text = ' '.join(text_parts).lower()

        # German umlauts/ß are a strong signal
        if any(c in text for c in german_chars):
            return 'de'

        # Check for common German words
        words = set(re.split(r'\W+', text))
        if len(words & german_words) >= 2:
            return 'de'

        return 'en'

    def _t(self, key: str, **kwargs) -> str:
        """Get localized UI text."""
        texts = self.UI_TEXTS.get(self.lang, self.UI_TEXTS['en'])
        text = texts.get(key, self.UI_TEXTS['en'].get(key, key))
        if kwargs:
            text = text.format(**kwargs)
        return text

    # ================================================================
    # Naming helpers — MUST match TypeScriptGenerator exactly
    # ================================================================

    def _to_pascal_case(self, text: str) -> str:
        text = text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        return "".join(word.capitalize() for word in re.sub(r"[^a-zA-Z0-9]", " ", text).split())

    def _to_singular(self, pascal_name: str) -> str:
        return pascal_name[:-1] if pascal_name.endswith("s") else f"{pascal_name}Entry"

    def _to_const_name(self, identifier: str) -> str:
        name = identifier.upper().replace("-", "_").replace("&", "").replace(" ", "_")
        return re.sub(r"_+", "_", name)

    # ================================================================
    # Analysis helpers
    # ================================================================

    def _get_display_field(self, identifier: str) -> str:
        """Which field to show for an entity in dropdowns / table lookups."""
        if identifier not in self.apps:
            return "record_id"
        controls = self.apps[identifier].get("controls", {})

        for key, ctrl in controls.items():
            if ctrl.get("fulltype") == "string/text" and ctrl.get("in_list"):
                return key
        for name in ["name", "title", "bezeichnung", "label", "titel", "description"]:
            if name in controls:
                return name
        for key, ctrl in controls.items():
            if "string" in ctrl.get("fulltype", ""):
                return key
        return next(iter(controls.keys()), "record_id")

    @staticmethod
    def _normalize_for_icon_match(text: str) -> str:
        """Collapse umlauts and ae/oe/ue digraphs to base vowels for fuzzy icon matching."""
        text = text.replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("ß", "ss")
        text = text.replace("ae", "a").replace("oe", "o").replace("ue", "u")
        return text

    def _get_icon_name(self, identifier: str) -> str:
        lower = identifier.lower()
        norm_id = self._normalize_for_icon_match(lower)
        for keyword, icon in self.ICON_MAP.items():
            # Direct match first, then normalized match
            if keyword in lower:
                return icon
            norm_kw = self._normalize_for_icon_match(keyword)
            if norm_kw in norm_id:
                return icon
        return "FileText"

    def _get_applookup_deps(self, identifier: str) -> list:
        """All applookup fields and their target entities for a given entity."""
        deps = []
        if identifier not in self.apps:
            return deps
        controls = self.apps[identifier].get("controls", {})
        for ctrl_key, ctrl_data in controls.items():
            if "applookup" not in ctrl_data.get("fulltype", ""):
                continue
            lookup_app_url = ctrl_data.get("lookup_app", "")
            if not lookup_app_url:
                continue
            try:
                target_app_id = lookup_app_url.rstrip("/").split("/")[-1]
                target_identifier = self.app_id_to_identifier.get(target_app_id)
                if target_identifier:
                    deps.append({
                        "ctrl_key": ctrl_key,
                        "target_identifier": target_identifier,
                        "target_pascal": self._to_pascal_case(target_identifier),
                        "target_const": self._to_const_name(target_identifier),
                        "display_field": self._get_display_field(target_identifier),
                    })
            except Exception:
                pass
        return deps

    def _get_unique_applookup_entities(self, identifier: str) -> list:
        """Deduplicated target entities (one entry per referenced entity)."""
        deps = self._get_applookup_deps(identifier)
        seen = {}
        for dep in deps:
            t = dep["target_identifier"]
            if t not in seen:
                seen[t] = dep
        return list(seen.values())

    def _has_date_fields(self, identifier: str) -> bool:
        """Check if entity has any date/datetime fields."""
        if identifier not in self.apps:
            return False
        controls = self.apps[identifier].get("controls", {})
        return any('date' in c.get('fulltype', '') for c in controls.values())

    # ================================================================
    # Main entry point
    # ================================================================

    def generate_all(self) -> dict:
        """Returns {filepath: content} for all files to generate."""
        files = {}

        files["src/App.tsx"] = self._generate_app_router()
        files["src/components/Layout.tsx"] = self._generate_layout()
        files["src/components/PageShell.tsx"] = self._generate_page_shell()
        files["src/pages/DashboardOverview.tsx"] = self._generate_overview()
        files["src/components/ConfirmDialog.tsx"] = self._generate_confirm_dialog()
        files["src/components/StatCard.tsx"] = self._generate_stat_card()

        for identifier in self.crud_scaffolds:
            pascal = self._to_pascal_case(identifier)
            files[f"src/pages/{pascal}Page.tsx"] = self._generate_entity_page(identifier)
            files[f"src/components/dialogs/{pascal}Dialog.tsx"] = self._generate_entity_dialog(identifier)

        # Placeholder pages for non-scaffolded entities
        for identifier in self.apps:
            if identifier not in self.crud_scaffolds:
                pascal = self._to_pascal_case(identifier)
                files[f"src/pages/{pascal}Page.tsx"] = self._generate_placeholder_page(identifier)

        return files

    # ================================================================
    # PageShell.tsx — Consistent page header wrapper
    # ================================================================

    def _generate_page_shell(self) -> str:
        return """import type { ReactNode } from 'react';

interface PageShellProps {
  title: string;
  subtitle: string;
  action?: ReactNode;
  children: ReactNode;
}

export function PageShell({ title, subtitle, action, children }: PageShellProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            {title}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>
        </div>
        {action}
      </div>
      {children}
    </div>
  );
}"""

    # ================================================================
    # App.tsx — Router with all routes
    # ================================================================

    def _generate_app_router(self) -> str:
        L = []
        L.append("import { BrowserRouter, Routes, Route } from 'react-router-dom';")
        L.append("import { Layout } from '@/components/Layout';")
        L.append("import DashboardOverview from '@/pages/DashboardOverview';")

        for identifier in self.apps:
            pascal = self._to_pascal_case(identifier)
            L.append("import " + pascal + "Page from '@/pages/" + pascal + "Page';")

        L.append("")
        L.append("export default function App() {")
        L.append("  return (")
        L.append("    <BrowserRouter basename={import.meta.env.BASE_URL}>")
        L.append("      <Routes>")
        L.append("        <Route element={<Layout />}>")
        L.append("          <Route index element={<DashboardOverview />} />")

        for identifier in self.apps:
            pascal = self._to_pascal_case(identifier)
            route_path = identifier.replace("_", "-")
            L.append('          <Route path="' + route_path + '" element={<' + pascal + 'Page />} />')

        L.append("        </Route>")
        L.append("      </Routes>")
        L.append("    </BrowserRouter>")
        L.append("  );")
        L.append("}")
        return "\n".join(L)

    # ================================================================
    # Layout.tsx — Polished sidebar navigation + Outlet
    # Uses semantic sidebar tokens (bg-sidebar, text-sidebar-foreground, etc.)
    # so it adapts to whatever the agent puts in index.css
    # ================================================================

    def _generate_layout(self) -> str:
        # Collect all icon names
        icons = {"LayoutDashboard", "Menu", "X"}
        for identifier in self.apps:
            icons.add(self._get_icon_name(identifier))

        overview_label = self._t('overview')
        management_label = self._t('management')
        nav_label = self._t('navigation')

        # Use first entity's icon for the logo
        first_icon = self._get_icon_name(next(iter(self.apps), ""))

        L = []
        L.append("import { NavLink, Outlet } from 'react-router-dom';")
        L.append("import { " + ", ".join(sorted(icons)) + " } from 'lucide-react';")
        L.append("import { useState } from 'react';")
        L.append("")

        # App identity constants — agent customizes these
        L.append("// ⚡ Customize these for your app")
        L.append("const APP_TITLE = 'Dashboard';")
        L.append("const APP_SUBTITLE = '" + management_label + "';")
        L.append("")

        # Navigation config
        L.append("const navigation = [")
        L.append("  { name: '" + overview_label + "', href: '/', icon: LayoutDashboard },")
        for identifier in self.apps:
            label = self.apps[identifier].get("name", self._to_pascal_case(identifier))
            icon = self._get_icon_name(identifier)
            route_path = "/" + identifier.replace("_", "-")
            L.append("  { name: '" + label + "', href: '" + route_path + "', icon: " + icon + " },")
        L.append("];")
        L.append("")

        L.append("export function Layout() {")
        L.append("  const [sidebarOpen, setSidebarOpen] = useState(false);")
        L.append("")
        L.append("  return (")
        L.append('    <div className="min-h-screen bg-background">')

        # Mobile overlay
        L.append("      {sidebarOpen && (")
        L.append('        <div')
        L.append('          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"')
        L.append("          onClick={() => setSidebarOpen(false)}")
        L.append("        />")
        L.append("      )}")

        # Sidebar with semantic sidebar tokens
        L.append("")
        L.append("      <aside")
        L.append("        className={`")
        L.append("          fixed top-0 left-0 z-50 h-full w-64 bg-sidebar border-r border-sidebar-border")
        L.append("          transform transition-transform duration-200 ease-in-out")
        L.append("          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}")
        L.append("          lg:translate-x-0")
        L.append("        `}")
        L.append("      >")

        # Logo area
        L.append('        <div className="flex items-center justify-between px-5 py-6 border-b border-sidebar-border">')
        L.append('          <div className="flex items-center gap-3">')
        L.append('            <div className="w-9 h-9 rounded-xl bg-sidebar-primary flex items-center justify-center shadow-sm">')
        L.append('              <' + first_icon + ' size={16} className="text-sidebar-primary-foreground" />')
        L.append("            </div>")
        L.append("            <div>")
        L.append('              <h1 className="text-sm font-bold tracking-tight text-sidebar-foreground">{APP_TITLE}</h1>')
        L.append('              <p className="text-xs text-sidebar-foreground/60">{APP_SUBTITLE}</p>')
        L.append("            </div>")
        L.append("          </div>")
        L.append('          <button')
        L.append('            className="lg:hidden p-1.5 rounded-lg text-sidebar-foreground/60 hover:text-sidebar-foreground transition-colors"')
        L.append("            onClick={() => setSidebarOpen(false)}")
        L.append("          >")
        L.append('            <X size={16} />')
        L.append("          </button>")
        L.append("        </div>")

        # Navigation links with proper TypeScript
        L.append('        <nav className="px-3 pt-4 space-y-0.5">')
        L.append('          <p className="px-3 pb-2 text-xs font-semibold uppercase tracking-widest text-sidebar-foreground/40">')
        L.append("            " + nav_label)
        L.append("          </p>")
        L.append("          {navigation.map(item => (")
        L.append("            <NavLink")
        L.append("              key={item.href}")
        L.append("              to={item.href}")
        L.append("              end={item.href === '/'}")
        L.append("              onClick={() => setSidebarOpen(false)}")
        L.append("              className={({ isActive }: { isActive: boolean }) =>")
        L.append("                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${")
        L.append("                  isActive")
        L.append("                    ? 'bg-sidebar-primary text-sidebar-primary-foreground shadow-sm'")
        L.append("                    : 'text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'")
        L.append("                }`")
        L.append("              }")
        L.append("            >")
        L.append('              <item.icon size={16} className="shrink-0" />')
        L.append("              {item.name}")
        L.append("            </NavLink>")
        L.append("          ))}")
        L.append("        </nav>")
        L.append("      </aside>")
        L.append("")

        # Main content
        L.append('      <div className="lg:pl-64">')
        L.append('        <header className="lg:hidden flex items-center gap-4 px-4 py-3 border-b bg-card sticky top-0 z-30">')
        L.append('          <button')
        L.append('            className="p-2 rounded-lg hover:bg-accent transition-colors"')
        L.append("            onClick={() => setSidebarOpen(true)}")
        L.append("          >")
        L.append('            <Menu size={18} />')
        L.append("          </button>")
        L.append('          <span className="font-semibold text-sm">{APP_TITLE}</span>')
        L.append("        </header>")
        L.append('        <main className="p-6 lg:p-8 max-w-screen-2xl">')
        L.append("          <Outlet />")
        L.append("        </main>")
        L.append("      </div>")

        L.append("    </div>")
        L.append("  );")
        L.append("}")
        return "\n".join(L)

    # ================================================================
    # DashboardOverview.tsx — Placeholder for agent to customize
    # ================================================================

    def _generate_overview(self) -> str:
        L = []
        L.append("import { useEffect, useState } from 'react';")
        L.append("import { StatCard } from '@/components/StatCard';")
        L.append("import { LivingAppsService } from '@/services/livingAppsService';")

        # Import types for all entities
        type_names = [self._to_pascal_case(k) for k in self.apps]
        if type_names:
            L.append("import type { " + ", ".join(type_names) + " } from '@/types/app';")
        L.append("")

        L.append("export default function DashboardOverview() {")

        # Generate state for each entity count
        for identifier in self.apps:
            pascal = self._to_pascal_case(identifier)
            L.append("  const [" + identifier + "Count, set" + pascal + "Count] = useState(0);")
        L.append("  const [loading, setLoading] = useState(true);")
        L.append("")

        # Load counts
        L.append("  useEffect(() => {")
        L.append("    async function loadStats() {")
        L.append("      try {")
        L.append("        const [" + ", ".join(identifier + "Data" for identifier in self.apps) + "] = await Promise.all([")
        for identifier in self.apps:
            pascal = self._to_pascal_case(identifier)
            L.append("          LivingAppsService.get" + pascal + "(),")
        L.append("        ]);")
        for identifier in self.apps:
            pascal = self._to_pascal_case(identifier)
            L.append("        set" + pascal + "Count(" + identifier + "Data.length);")
        L.append("      } catch (e) {")
        L.append("        console.error('Failed to load stats:', e);")
        L.append("      } finally {")
        L.append("        setLoading(false);")
        L.append("      }")
        L.append("    }")
        L.append("    loadStats();")
        L.append("  }, []);")
        L.append("")

        L.append("  return (")
        L.append('    <div className="space-y-8">')

        # Hero section
        L.append('      {/* === HERO SECTION — Customize with gradient, welcome text, key metrics === */}')
        L.append("      <div>")
        L.append('        <h1 className="text-3xl font-bold tracking-tight">' + self._t('welcome') + '</h1>')
        L.append("        <p className=\"text-muted-foreground mt-1\">" + self._t('overview_subtitle') + "</p>")
        L.append("      </div>")
        L.append("")

        # KPI cards
        L.append('      {/* === KPI CARDS — Customize with icons, colors, descriptions === */}')
        cols = str(min(len(self.apps), 5))
        L.append('      <div className="grid grid-cols-2 lg:grid-cols-' + cols + ' gap-4">')
        for identifier in self.apps:
            pascal = self._to_pascal_case(identifier)
            label = self.apps[identifier].get("name", pascal)
            L.append("        <StatCard")
            L.append('          title="' + label + '"')
            L.append("          value={loading ? '...' : " + identifier + "Count}")
            L.append('          description="' + self._t('in_system', entity=label) + '"')
            L.append("        />")
        L.append("      </div>")
        L.append("")

        # Charts/content placeholder
        L.append('      {/* === CHARTS / CONTENT — Build your dashboard here === */}')
        L.append('      {/* Ideas: recharts BarChart/LineChart, upcoming items list, recent activity feed */}')

        L.append("    </div>")
        L.append("  );")
        L.append("}")
        return "\n".join(L)

    # ================================================================
    # ConfirmDialog.tsx — Generic delete confirmation
    # ================================================================

    def _generate_confirm_dialog(self) -> str:
        cancel = self._t('cancel')
        delete = self._t('delete')
        return f"""import {{
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
}} from '@/components/ui/dialog';
import {{ Button }} from '@/components/ui/button';

interface ConfirmDialogProps {{
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description: string;
}}

export function ConfirmDialog({{ open, onClose, onConfirm, title, description }}: ConfirmDialogProps) {{
  return (
    <Dialog open={{open}} onOpenChange={{v => !v && onClose()}}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{title}}</DialogTitle>
          <DialogDescription>{{description}}</DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={{onClose}}>{cancel}</Button>
          <Button variant="destructive" onClick={{onConfirm}}>{delete}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}}"""

    # ================================================================
    # StatCard.tsx — Reusable KPI card
    # ================================================================

    def _generate_stat_card(self) -> str:
        return """interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ReactNode;
}

export function StatCard({ title, value, description, icon }: StatCardProps) {
  return (
    <div className="rounded-xl border bg-card p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        {icon}
      </div>
      <p className="text-3xl font-bold mt-2">{value}</p>
      {description && (
        <p className="text-xs text-muted-foreground mt-1">{description}</p>
      )}
    </div>
  );
}"""

    # ================================================================
    # {Entity}Page.tsx — Full CRUD page per scaffolded entity
    # ================================================================

    def _generate_entity_page(self, identifier: str) -> str:
        app_data = self.apps[identifier]
        controls = app_data.get("controls", {})
        pascal = self._to_pascal_case(identifier)
        singular = self._to_singular(pascal)
        label = app_data.get("name", pascal)

        deps = self._get_applookup_deps(identifier)
        unique_deps = self._get_unique_applookup_entities(identifier)

        has_lookup = any(c.get("fulltype") == "lookup/select" for c in controls.values())
        has_dates = self._has_date_fields(identifier)
        col_count = len(controls) + 1  # +1 for actions

        L = []

        # --- Imports ---
        L.append("import { useState, useEffect } from 'react';")
        L.append("import { LivingAppsService, extractRecordId, createRecordUrl } from '@/services/livingAppsService';")

        type_imports = [pascal]
        for dep in unique_deps:
            if dep["target_pascal"] not in type_imports:
                type_imports.append(dep["target_pascal"])
        L.append("import type { " + ", ".join(type_imports) + " } from '@/types/app';")
        L.append("import { APP_IDS } from '@/types/app';")
        L.append("import { Button } from '@/components/ui/button';")
        L.append("import { Input } from '@/components/ui/input';")
        L.append("import {")
        L.append("  Table, TableBody, TableCell, TableHead,")
        L.append("  TableHeader, TableRow,")
        L.append("} from '@/components/ui/table';")
        if has_lookup:
            L.append("import { Badge } from '@/components/ui/badge';")
        L.append("import { Pencil, Trash2, Plus, Search } from 'lucide-react';")
        L.append("import { " + pascal + "Dialog } from '@/components/dialogs/" + pascal + "Dialog';")
        L.append("import { ConfirmDialog } from '@/components/ConfirmDialog';")
        L.append("import { PageShell } from '@/components/PageShell';")
        if has_dates:
            L.append("import { format, parseISO } from 'date-fns';")
            if self.lang == 'de':
                L.append("import { de } from 'date-fns/locale';")
        L.append("")

        # Date format helper (only if needed)
        if has_dates:
            date_fmt = self._t('date_format')
            if self.lang == 'de':
                L.append("function formatDate(d?: string) {")
                L.append("  if (!d) return '—';")
                L.append("  try { return format(parseISO(d), '" + date_fmt + "', { locale: de }); } catch { return d; }")
                L.append("}")
                L.append("")
            else:
                L.append("function formatDate(d?: string) {")
                L.append("  if (!d) return '—';")
                L.append("  try { return format(parseISO(d), '" + date_fmt + "'); } catch { return d; }")
                L.append("}")
                L.append("")

        # --- Component ---
        L.append("export default function " + pascal + "Page() {")
        L.append("  const [records, setRecords] = useState<" + pascal + "[]>([]);")
        L.append("  const [loading, setLoading] = useState(true);")
        L.append("  const [search, setSearch] = useState('');")
        L.append("  const [dialogOpen, setDialogOpen] = useState(false);")
        L.append("  const [editingRecord, setEditingRecord] = useState<" + pascal + " | null>(null);")
        L.append("  const [deleteTarget, setDeleteTarget] = useState<" + pascal + " | null>(null);")

        for dep in unique_deps:
            L.append("  const [" + dep["target_identifier"] + "List, set" + dep["target_pascal"] + "List] = useState<" + dep["target_pascal"] + "[]>([]);")

        L.append("")
        L.append("  useEffect(() => { loadData(); }, []);")
        L.append("")

        # loadData
        L.append("  async function loadData() {")
        L.append("    setLoading(true);")
        L.append("    try {")
        if unique_deps:
            vars_list = ["mainData"]
            calls_list = ["LivingAppsService.get" + pascal + "()"]
            for dep in unique_deps:
                vars_list.append(dep["target_identifier"] + "Data")
                calls_list.append("LivingAppsService.get" + dep["target_pascal"] + "()")
            L.append("      const [" + ", ".join(vars_list) + "] = await Promise.all([")
            for call in calls_list:
                L.append("        " + call + ",")
            L.append("      ]);")
            L.append("      setRecords(mainData);")
            for dep in unique_deps:
                L.append("      set" + dep["target_pascal"] + "List(" + dep["target_identifier"] + "Data);")
        else:
            L.append("      setRecords(await LivingAppsService.get" + pascal + "());")
        L.append("    } finally {")
        L.append("      setLoading(false);")
        L.append("    }")
        L.append("  }")
        L.append("")

        # CRUD handlers
        L.append("  async function handleCreate(fields: " + pascal + "['fields']) {")
        L.append("    await LivingAppsService.create" + singular + "(fields);")
        L.append("    await loadData();")
        L.append("    setDialogOpen(false);")
        L.append("  }")
        L.append("")
        L.append("  async function handleUpdate(fields: " + pascal + "['fields']) {")
        L.append("    if (!editingRecord) return;")
        L.append("    await LivingAppsService.update" + singular + "(editingRecord.record_id, fields);")
        L.append("    await loadData();")
        L.append("    setEditingRecord(null);")
        L.append("  }")
        L.append("")
        L.append("  async function handleDelete() {")
        L.append("    if (!deleteTarget) return;")
        L.append("    await LivingAppsService.delete" + singular + "(deleteTarget.record_id);")
        L.append("    setRecords(prev => prev.filter(r => r.record_id !== deleteTarget.record_id));")
        L.append("    setDeleteTarget(null);")
        L.append("  }")
        L.append("")

        # Applookup display helpers (deduplicated)
        generated_helpers = set()
        for dep in deps:
            helper_name = "get" + dep["target_pascal"] + "DisplayName"
            if helper_name in generated_helpers:
                continue
            generated_helpers.add(helper_name)
            L.append("  function " + helper_name + "(url?: string) {")
            L.append("    if (!url) return '—';")
            L.append("    const id = extractRecordId(url);")
            L.append("    return " + dep["target_identifier"] + "List.find(r => r.record_id === id)?.fields." + dep["display_field"] + " ?? '—';")
            L.append("  }")
            L.append("")

        # Search filter
        L.append("  const filtered = records.filter(r => {")
        L.append("    if (!search) return true;")
        L.append("    const s = search.toLowerCase();")
        L.append("    return Object.values(r.fields).some(v =>")
        L.append("      String(v ?? '').toLowerCase().includes(s)")
        L.append("    );")
        L.append("  });")
        L.append("")

        # Loading state
        L.append("  if (loading) {")
        L.append("    return (")
        L.append('      <div className="flex items-center justify-center py-32">')
        L.append('        <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full" />')
        L.append("      </div>")
        L.append("    );")
        L.append("  }")
        L.append("")

        # --- Render with PageShell ---
        search_ph = self._t('search_entity', entity=label)
        add_btn = self._t('add')
        actions_label = self._t('actions')
        no_results = self._t('no_results')
        no_data = self._t('no_data_yet', entity=label)
        delete_title = self._t('delete_entity', entity=label)
        delete_desc = self._t('confirm_delete_desc')

        L.append("  return (")
        L.append("    <PageShell")
        L.append('      title="' + label + '"')
        L.append("      subtitle={`${records.length} " + self._t('in_system', entity=label) + "`}")
        L.append("      action={")
        L.append('        <Button onClick={() => setDialogOpen(true)} className="shrink-0">')
        L.append('          <Plus className="h-4 w-4 mr-2" /> ' + add_btn)
        L.append("        </Button>")
        L.append("      }")
        L.append("    >")

        # Search bar
        L.append('      <div className="relative w-full max-w-sm">')
        L.append('        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />')
        L.append("        <Input")
        L.append('          placeholder="' + search_ph + '"')
        L.append("          value={search}")
        L.append("          onChange={e => setSearch(e.target.value)}")
        L.append('          className="pl-9"')
        L.append("        />")
        L.append("      </div>")

        # Table with card-like wrapper
        L.append('      <div className="rounded-lg border bg-card overflow-hidden">')
        L.append("        <Table>")
        L.append("          <TableHeader>")
        L.append("            <TableRow>")
        for ctrl_key, ctrl_data in controls.items():
            col_label = ctrl_data.get("label", ctrl_key)
            L.append('              <TableHead>' + col_label + '</TableHead>')
        L.append('              <TableHead className="w-24">' + actions_label + '</TableHead>')
        L.append("            </TableRow>")
        L.append("          </TableHeader>")
        L.append("          <TableBody>")
        L.append("            {filtered.map(record => (")
        L.append('              <TableRow key={record.record_id} className="hover:bg-muted/50 transition-colors">')

        # Table cells
        is_first_text = True
        for ctrl_key, ctrl_data in controls.items():
            fulltype = ctrl_data.get("fulltype", "string/text")
            cell = self._render_table_cell(ctrl_key, ctrl_data, fulltype, deps, is_first_text)
            L.append("                " + cell)
            if fulltype in ("string/text", "string/email") and is_first_text:
                is_first_text = False

        # Actions column
        L.append("                <TableCell>")
        L.append('                  <div className="flex gap-1">')
        L.append('                    <Button variant="ghost" size="icon" onClick={() => setEditingRecord(record)}>')
        L.append('                      <Pencil className="h-4 w-4" />')
        L.append("                    </Button>")
        L.append('                    <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(record)}>')
        L.append('                      <Trash2 className="h-4 w-4 text-destructive" />')
        L.append("                    </Button>")
        L.append("                  </div>")
        L.append("                </TableCell>")
        L.append("              </TableRow>")
        L.append("            ))}")

        # Empty state
        L.append("            {filtered.length === 0 && (")
        L.append("              <TableRow>")
        L.append('                <TableCell colSpan={' + str(col_count) + '} className="text-center py-16 text-muted-foreground">')
        L.append("                  {search ? '" + no_results + "' : '" + no_data + "'}")
        L.append("                </TableCell>")
        L.append("              </TableRow>")
        L.append("            )}")
        L.append("          </TableBody>")
        L.append("        </Table>")
        L.append("      </div>")

        # Dialogs
        L.append("")
        L.append("      <" + pascal + "Dialog")
        L.append("        open={dialogOpen || !!editingRecord}")
        L.append("        onClose={() => { setDialogOpen(false); setEditingRecord(null); }}")
        L.append("        onSubmit={editingRecord ? handleUpdate : handleCreate}")
        L.append("        defaultValues={editingRecord?.fields}")
        for dep in unique_deps:
            L.append("        " + dep["target_identifier"] + "List={" + dep["target_identifier"] + "List}")
        L.append("      />")
        L.append("")
        L.append("      <ConfirmDialog")
        L.append("        open={!!deleteTarget}")
        L.append("        onClose={() => setDeleteTarget(null)}")
        L.append("        onConfirm={handleDelete}")
        L.append('        title="' + delete_title + '"')
        L.append('        description="' + delete_desc + '"')
        L.append("      />")

        L.append("    </PageShell>")
        L.append("  );")
        L.append("}")
        return "\n".join(L)

    # ================================================================
    # Table cell renderer helper
    # ================================================================

    def _render_table_cell(self, ctrl_key: str, ctrl_data: dict, fulltype: str, deps: list, is_first_text: bool) -> str:
        yes_text = self._t('yes')
        no_text = self._t('no')

        if fulltype == "string/textarea":
            return '<TableCell className="max-w-xs"><span className="truncate block">{record.fields.' + ctrl_key + " ?? '—'}</span></TableCell>"
        elif fulltype == "bool":
            return ("<TableCell>"
                    '<span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${'
                    "record.fields." + ctrl_key + " ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'"
                    "}`}>"
                    "{record.fields." + ctrl_key + " ? '" + yes_text + "' : '" + no_text + "'}"
                    "</span></TableCell>")
        elif fulltype == "lookup/select":
            return '<TableCell><Badge variant="secondary">{record.fields.' + ctrl_key + " ?? '—'}</Badge></TableCell>"
        elif "applookup" in fulltype:
            dep = next((d for d in deps if d["ctrl_key"] == ctrl_key), None)
            if dep:
                helper = "get" + dep["target_pascal"] + "DisplayName"
                return "<TableCell>{" + helper + "(record.fields." + ctrl_key + ")}</TableCell>"
            return "<TableCell>{record.fields." + ctrl_key + " ?? '—'}</TableCell>"
        elif "date" in fulltype:
            return '<TableCell className="text-muted-foreground">{formatDate(record.fields.' + ctrl_key + ")}</TableCell>"
        elif is_first_text and fulltype in ("string/text", "string/email"):
            return '<TableCell className="font-medium">{record.fields.' + ctrl_key + " ?? '—'}</TableCell>"
        elif fulltype == "number":
            return "<TableCell>{record.fields." + ctrl_key + " ?? '—'}</TableCell>"
        else:
            return "<TableCell>{record.fields." + ctrl_key + " ?? '—'}</TableCell>"

    # ================================================================
    # {Entity}Dialog.tsx — Create/edit dialog per scaffolded entity
    # ================================================================

    def _generate_entity_dialog(self, identifier: str) -> str:
        app_data = self.apps[identifier]
        controls = app_data.get("controls", {})
        pascal = self._to_pascal_case(identifier)
        label = app_data.get("name", pascal)

        deps = self._get_applookup_deps(identifier)
        unique_deps = self._get_unique_applookup_entities(identifier)

        # Determine which shadcn imports are needed
        has_textarea = any(c.get("fulltype") == "string/textarea" for c in controls.values())
        has_select = any(c.get("fulltype") in ("lookup/select",) or "applookup" in c.get("fulltype", "") for c in controls.values())
        has_checkbox = any(c.get("fulltype") == "bool" for c in controls.values())

        # Localized text
        cancel_text = self._t('cancel')
        saving_text = self._t('saving')
        save_text = self._t('save')
        create_text = self._t('create')
        edit_title = self._t('edit_entity', entity=label)
        new_title = self._t('new_entity', entity=label)
        select_ph = self._t('select_placeholder')

        L = []

        # --- Imports ---
        L.append("import { useState, useEffect } from 'react';")

        type_imports = [pascal]
        for dep in unique_deps:
            if dep["target_pascal"] not in type_imports:
                type_imports.append(dep["target_pascal"])
        L.append("import type { " + ", ".join(type_imports) + " } from '@/types/app';")
        L.append("import { APP_IDS } from '@/types/app';")
        L.append("import { extractRecordId, createRecordUrl } from '@/services/livingAppsService';")
        L.append("import {")
        L.append("  Dialog, DialogContent, DialogHeader,")
        L.append("  DialogTitle, DialogFooter,")
        L.append("} from '@/components/ui/dialog';")
        L.append("import { Button } from '@/components/ui/button';")
        L.append("import { Input } from '@/components/ui/input';")
        L.append("import { Label } from '@/components/ui/label';")
        if has_textarea:
            L.append("import { Textarea } from '@/components/ui/textarea';")
        if has_select:
            L.append("import {")
            L.append("  Select, SelectContent, SelectItem,")
            L.append("  SelectTrigger, SelectValue,")
            L.append("} from '@/components/ui/select';")
        if has_checkbox:
            L.append("import { Checkbox } from '@/components/ui/checkbox';")
        L.append("")

        # --- Props interface ---
        L.append("interface " + pascal + "DialogProps {")
        L.append("  open: boolean;")
        L.append("  onClose: () => void;")
        L.append("  onSubmit: (fields: " + pascal + "['fields']) => Promise<void>;")
        L.append("  defaultValues?: " + pascal + "['fields'];")
        for dep in unique_deps:
            L.append("  " + dep["target_identifier"] + "List: " + dep["target_pascal"] + "[];")
        L.append("}")
        L.append("")

        # --- Component ---
        props_destructure = "open, onClose, onSubmit, defaultValues"
        for dep in unique_deps:
            props_destructure += ", " + dep["target_identifier"] + "List"

        L.append("export function " + pascal + "Dialog({ " + props_destructure + " }: " + pascal + "DialogProps) {")
        L.append("  const [fields, setFields] = useState<Partial<" + pascal + "['fields']>>({});")
        L.append("  const [saving, setSaving] = useState(false);")
        L.append("")
        L.append("  useEffect(() => {")
        L.append("    if (open) setFields(defaultValues ?? {});")
        L.append("  }, [open, defaultValues]);")
        L.append("")
        L.append("  async function handleSubmit(e: React.FormEvent) {")
        L.append("    e.preventDefault();")
        L.append("    setSaving(true);")
        L.append("    try {")
        L.append("      await onSubmit(fields as " + pascal + "['fields']);")
        L.append("    } finally {")
        L.append("      setSaving(false);")
        L.append("    }")
        L.append("  }")
        L.append("")

        # --- Render ---
        L.append("  return (")
        L.append("    <Dialog open={open} onOpenChange={v => !v && onClose()}>")
        L.append('      <DialogContent className="max-w-lg">')
        L.append("        <DialogHeader>")
        L.append("          <DialogTitle>{defaultValues ? '" + edit_title + "' : '" + new_title + "'}</DialogTitle>")
        L.append("        </DialogHeader>")
        L.append('        <form onSubmit={handleSubmit} className="space-y-4">')

        # Form fields
        for ctrl_key, ctrl_data in controls.items():
            fulltype = ctrl_data.get("fulltype", "string/text")
            field_label = ctrl_data.get("label", ctrl_key)
            required = ctrl_data.get("required", False)
            req_mark = " *" if required else ""
            req_attr = " required" if required else ""

            L.append('          <div className="space-y-2">')
            L.append('            <Label htmlFor="' + ctrl_key + '">' + field_label + req_mark + '</Label>')

            field_jsx = self._render_form_field(ctrl_key, ctrl_data, fulltype, deps, unique_deps, req_attr, select_ph)
            for line in field_jsx:
                L.append("            " + line)

            L.append("          </div>")

        # Footer
        L.append("          <DialogFooter>")
        L.append('            <Button type="button" variant="outline" onClick={onClose}>' + cancel_text + '</Button>')
        L.append('            <Button type="submit" disabled={saving}>')
        L.append("              {saving ? '" + saving_text + "' : defaultValues ? '" + save_text + "' : '" + create_text + "'}")
        L.append("            </Button>")
        L.append("          </DialogFooter>")
        L.append("        </form>")
        L.append("      </DialogContent>")
        L.append("    </Dialog>")
        L.append("  );")
        L.append("}")
        return "\n".join(L)

    # ================================================================
    # Form field renderer helper
    # ================================================================

    def _render_form_field(self, ctrl_key: str, ctrl_data: dict, fulltype: str, deps: list, unique_deps: list, req_attr: str, select_ph: str) -> list:
        """Returns a list of JSX lines for a single form field."""
        lines = []

        if fulltype == "string/text":
            lines.append("<Input")
            lines.append('  id="' + ctrl_key + '"')
            lines.append("  value={fields." + ctrl_key + " ?? ''}")
            lines.append("  onChange={e => setFields(f => ({ ...f, " + ctrl_key + ": e.target.value }))}")
            if req_attr.strip():
                lines.append("  required")
            lines.append("/>")

        elif fulltype == "string/textarea":
            lines.append("<Textarea")
            lines.append('  id="' + ctrl_key + '"')
            lines.append("  value={fields." + ctrl_key + " ?? ''}")
            lines.append("  onChange={e => setFields(f => ({ ...f, " + ctrl_key + ": e.target.value }))}")
            lines.append('  rows={3}')
            lines.append("/>")

        elif fulltype == "string/email":
            lines.append("<Input")
            lines.append('  id="' + ctrl_key + '"')
            lines.append('  type="email"')
            lines.append("  value={fields." + ctrl_key + " ?? ''}")
            lines.append("  onChange={e => setFields(f => ({ ...f, " + ctrl_key + ": e.target.value }))}")
            lines.append("/>")

        elif fulltype == "number":
            lines.append("<Input")
            lines.append('  id="' + ctrl_key + '"')
            lines.append('  type="number"')
            lines.append("  value={fields." + ctrl_key + " ?? ''}")
            lines.append("  onChange={e => setFields(f => ({ ...f, " + ctrl_key + ": e.target.value ? Number(e.target.value) : undefined }))}")
            lines.append("/>")

        elif fulltype == "bool":
            lines.append('<div className="flex items-center gap-2 pt-1">')
            lines.append("  <Checkbox")
            lines.append('    id="' + ctrl_key + '"')
            lines.append("    checked={!!fields." + ctrl_key + "}")
            lines.append("    onCheckedChange={(v) => setFields(f => ({ ...f, " + ctrl_key + ": !!v }))}")
            lines.append("  />")
            lines.append('  <Label htmlFor="' + ctrl_key + '" className="font-normal">' + ctrl_data.get("label", ctrl_key) + '</Label>')
            lines.append("</div>")

        elif fulltype == "date/date":
            lines.append("<Input")
            lines.append('  id="' + ctrl_key + '"')
            lines.append('  type="date"')
            lines.append("  value={fields." + ctrl_key + " ?? ''}")
            lines.append("  onChange={e => setFields(f => ({ ...f, " + ctrl_key + ": e.target.value }))}")
            if req_attr.strip():
                lines.append("  required")
            lines.append("/>")

        elif fulltype == "date/datetimeminute":
            lines.append("<Input")
            lines.append('  id="' + ctrl_key + '"')
            lines.append('  type="datetime-local"')
            lines.append('  step="60"')
            lines.append("  value={fields." + ctrl_key + " ?? ''}")
            lines.append("  onChange={e => setFields(f => ({ ...f, " + ctrl_key + ": e.target.value }))}")
            lines.append("/>")

        elif fulltype == "lookup/select":
            lookup_data = ctrl_data.get("lookup_data", {})
            # Build TypeScript union type assertion to match generated types
            if lookup_data:
                union_type = " | ".join("'" + k + "'" for k in lookup_data.keys())
                type_cast = " as " + union_type
            else:
                type_cast = ""
            lines.append("<Select")
            lines.append("  value={fields." + ctrl_key + " ?? 'none'}")
            lines.append("  onValueChange={v => setFields(f => ({ ...f, " + ctrl_key + ": v === 'none' ? undefined : v" + type_cast + " }))}")
            lines.append(">")
            lines.append('  <SelectTrigger id="' + ctrl_key + '"><SelectValue placeholder="' + select_ph + '" /></SelectTrigger>')
            lines.append("  <SelectContent>")
            lines.append('    <SelectItem value="none">—</SelectItem>')
            for key, value in lookup_data.items():
                safe_val = str(value).replace("'", "\\'")
                lines.append('    <SelectItem value="' + str(key) + '">' + safe_val + '</SelectItem>')
            lines.append("  </SelectContent>")
            lines.append("</Select>")

        elif "applookup" in fulltype:
            dep = next((d for d in deps if d["ctrl_key"] == ctrl_key), None)
            if dep:
                const_name = dep["target_const"]
                display_field = dep["display_field"]
                list_var = dep["target_identifier"] + "List"

                lines.append("<Select")
                lines.append("  value={extractRecordId(fields." + ctrl_key + ") ?? 'none'}")
                lines.append("  onValueChange={v => setFields(f => ({ ...f, " + ctrl_key + ": v === 'none' ? undefined : createRecordUrl(APP_IDS." + const_name + ", v) }))}")
                lines.append(">")
                lines.append('  <SelectTrigger id="' + ctrl_key + '"><SelectValue placeholder="' + select_ph + '" /></SelectTrigger>')
                lines.append("  <SelectContent>")
                lines.append('    <SelectItem value="none">—</SelectItem>')
                lines.append("    {" + list_var + ".map(r => (")
                lines.append('      <SelectItem key={r.record_id} value={r.record_id}>')
                lines.append("        {r.fields." + display_field + " ?? r.record_id}")
                lines.append("      </SelectItem>")
                lines.append("    ))}")
                lines.append("  </SelectContent>")
                lines.append("</Select>")
            else:
                lines.append("<Input")
                lines.append('  id="' + ctrl_key + '"')
                lines.append("  value={fields." + ctrl_key + " ?? ''}")
                lines.append("  onChange={e => setFields(f => ({ ...f, " + ctrl_key + ": e.target.value }))}")
                lines.append('  placeholder="Record URL"')
                lines.append("/>")

        else:
            # Fallback: text input
            lines.append("<Input")
            lines.append('  id="' + ctrl_key + '"')
            lines.append("  value={fields." + ctrl_key + " ?? ''}")
            lines.append("  onChange={e => setFields(f => ({ ...f, " + ctrl_key + ": e.target.value }))}")
            lines.append("/>")

        return lines

    # ================================================================
    # Placeholder page for non-scaffolded entities
    # ================================================================

    def _generate_placeholder_page(self, identifier: str) -> str:
        pascal = self._to_pascal_case(identifier)
        label = self.apps[identifier].get("name", pascal)

        L = []
        L.append("// TODO: Build custom UI for " + label)
        L.append("// This entity was not included in crud_scaffolds — build your own view here.")
        L.append("// Available: LivingAppsService.get" + pascal + "(), create/update/delete methods")
        L.append("")
        L.append("export default function " + pascal + "Page() {")
        L.append("  return (")
        L.append('    <div className="space-y-6">')
        L.append("      <div>")
        L.append('        <h1 className="text-2xl font-bold tracking-tight">' + label + "</h1>")
        L.append('        <p className="text-muted-foreground">Build your custom ' + label.lower() + ' view here.</p>')
        L.append("      </div>")
        L.append('      <div className="rounded-lg border border-dashed p-12 text-center text-muted-foreground">')
        L.append("        <p>Custom UI placeholder — build your " + label.lower() + " view here</p>")
        L.append("      </div>")
        L.append("    </div>")
        L.append("  );")
        L.append("}")
        return "\n".join(L)
