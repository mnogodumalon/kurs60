import { useEffect, useState } from 'react';
import { LivingAppsService } from '@/services/livingAppsService';
import type { Dozenten, Teilnehmer, Raeume, Kurse, Anmeldungen } from '@/types/app';
import { BookOpen, Users, GraduationCap, DoorOpen, ClipboardList, TrendingUp, Euro, CheckCircle2, Clock } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format, parseISO, isAfter, isBefore, startOfDay } from 'date-fns';
import { de } from 'date-fns/locale';
import { Link } from 'react-router-dom';

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle: string;
  icon: React.ReactNode;
  gradient: string;
  iconColor: string;
  href: string;
}

function KpiCard({ title, value, subtitle, icon, gradient, iconColor, href }: KpiCardProps) {
  return (
    <Link to={href} className="block">
      <div className={`rounded-2xl p-6 shadow-card border border-border/60 hover:shadow-elevated transition-smooth cursor-pointer ${gradient}`}>
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground tracking-wide">{title}</p>
            <p className="text-4xl font-bold mt-2 tabular-nums">{value}</p>
            <p className="text-xs text-muted-foreground mt-2">{subtitle}</p>
          </div>
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${iconColor}`}>
            {icon}
          </div>
        </div>
      </div>
    </Link>
  );
}

function HeroStatItem({ label, value, unit }: { label: string; value: string | number; unit?: string }) {
  return (
    <div className="text-center">
      <p className="text-3xl font-bold text-primary-foreground tabular-nums">
        {value}{unit && <span className="text-xl font-medium ml-1 opacity-80">{unit}</span>}
      </p>
      <p className="text-sm text-primary-foreground/70 mt-1 font-medium">{label}</p>
    </div>
  );
}

export default function DashboardOverview() {
  const [dozenten, setDozenten] = useState<Dozenten[]>([]);
  const [teilnehmer, setTeilnehmer] = useState<Teilnehmer[]>([]);
  const [raeume, setRaeume] = useState<Raeume[]>([]);
  const [kurse, setKurse] = useState<Kurse[]>([]);
  const [anmeldungen, setAnmeldungen] = useState<Anmeldungen[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        const [d, t, r, k, a] = await Promise.all([
          LivingAppsService.getDozenten(),
          LivingAppsService.getTeilnehmer(),
          LivingAppsService.getRaeume(),
          LivingAppsService.getKurse(),
          LivingAppsService.getAnmeldungen(),
        ]);
        setDozenten(d);
        setTeilnehmer(t);
        setRaeume(r);
        setKurse(k);
        setAnmeldungen(a);
      } catch (e) {
        console.error('Failed to load stats:', e);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  const today = startOfDay(new Date());

  const aktiveKurse = kurse.filter(k => {
    const start = k.fields.startdatum ? parseISO(k.fields.startdatum) : null;
    const end = k.fields.enddatum ? parseISO(k.fields.enddatum) : null;
    if (!start) return false;
    if (end) return !isAfter(start, today) && !isBefore(end, today);
    return !isAfter(start, today);
  });

  const kommendKurse = kurse.filter(k =>
    k.fields.startdatum ? isAfter(parseISO(k.fields.startdatum), today) : false
  );

  const bezahltCount = anmeldungen.filter(a => a.fields.bezahlt === true).length;
  const offenCount = anmeldungen.filter(a => !a.fields.bezahlt).length;

  const gesamtEinnahmen = anmeldungen
    .filter(a => a.fields.bezahlt)
    .reduce((sum, a) => {
      const kursRecord = kurse.find(k => a.fields.kurs && a.fields.kurs.includes(k.record_id));
      return sum + (kursRecord?.fields.preis ?? 0);
    }, 0);

  // Build monthly anmeldung chart (last 6 months)
  const monthlyData: { monat: string; anmeldungen: number }[] = [];
  for (let i = 5; i >= 0; i--) {
    const d = new Date();
    d.setMonth(d.getMonth() - i);
    const year = d.getFullYear();
    const month = d.getMonth();
    const label = format(d, 'MMM', { locale: de });
    const count = anmeldungen.filter(a => {
      if (!a.fields.anmeldedatum) return false;
      const date = parseISO(a.fields.anmeldedatum);
      return date.getFullYear() === year && date.getMonth() === month;
    }).length;
    monthlyData.push({ monat: label, anmeldungen: count });
  }

  // Recent anmeldungen (last 5)
  const recentAnmeldungen = [...anmeldungen]
    .sort((a, b) => {
      const da = a.fields.anmeldedatum ? parseISO(a.fields.anmeldedatum).getTime() : 0;
      const db = b.fields.anmeldedatum ? parseISO(b.fields.anmeldedatum).getTime() : 0;
      return db - da;
    })
    .slice(0, 5);

  const getTeilnehmerName = (url: string | undefined) => {
    if (!url) return '—';
    const id = url.split('/').pop();
    return teilnehmer.find(t => t.record_id === id)?.fields.name ?? '—';
  };

  const getKursTitle = (url: string | undefined) => {
    if (!url) return '—';
    const id = url.split('/').pop();
    return kurse.find(k => k.record_id === id)?.fields.titel ?? '—';
  };

  return (
    <div className="space-y-8">
      {/* Hero Banner */}
      <div className="rounded-2xl gradient-hero p-8 shadow-brand relative overflow-hidden">
        <div className="absolute inset-0 opacity-10"
          style={{ backgroundImage: 'radial-gradient(circle at 80% 50%, white 0%, transparent 60%)' }}
        />
        <div className="relative z-10">
          <p className="text-sm font-semibold text-primary-foreground/70 tracking-widest uppercase mb-2">Kursverwaltung</p>
          <h1 className="text-3xl font-bold text-primary-foreground tracking-tight">
            Willkommen im KursManager
          </h1>
          <p className="text-primary-foreground/70 mt-1 font-light">
            {loading ? 'Daten werden geladen…' : `${kurse.length} Kurse · ${teilnehmer.length} Teilnehmer · ${anmeldungen.length} Anmeldungen`}
          </p>
          <div className="mt-6 flex flex-wrap gap-10">
            <HeroStatItem label="Aktive Kurse" value={loading ? '—' : aktiveKurse.length} />
            <HeroStatItem label="Kommende Kurse" value={loading ? '—' : kommendKurse.length} />
            <HeroStatItem label="Unbezahlte Anmeldungen" value={loading ? '—' : offenCount} />
            <HeroStatItem
              label="Einnahmen gesamt"
              value={loading ? '—' : gesamtEinnahmen.toLocaleString('de-DE', { minimumFractionDigits: 0 })}
              unit="€"
            />
          </div>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        <KpiCard
          title="Kurse"
          value={loading ? '…' : kurse.length}
          subtitle="Gesamt angelegt"
          href="/kurse"
          gradient="gradient-card-blue bg-card"
          iconColor="bg-primary/10 text-primary"
          icon={<BookOpen size={20} />}
        />
        <KpiCard
          title="Teilnehmer"
          value={loading ? '…' : teilnehmer.length}
          subtitle="Registrierte Personen"
          href="/teilnehmer"
          gradient="gradient-card-teal bg-card"
          iconColor="bg-chart-2/15 text-chart-2"
          icon={<Users size={20} />}
        />
        <KpiCard
          title="Dozenten"
          value={loading ? '…' : dozenten.length}
          subtitle="Aktive Lehrkräfte"
          href="/dozenten"
          gradient="gradient-card-violet bg-card"
          iconColor="bg-chart-5/15 text-chart-5"
          icon={<GraduationCap size={20} />}
        />
        <KpiCard
          title="Räume"
          value={loading ? '…' : raeume.length}
          subtitle="Verfügbare Räumlichkeiten"
          href="/raeume"
          gradient="gradient-card-amber bg-card"
          iconColor="bg-chart-4/15 text-chart-4"
          icon={<DoorOpen size={20} />}
        />
        <KpiCard
          title="Anmeldungen"
          value={loading ? '…' : anmeldungen.length}
          subtitle={loading ? '—' : `${bezahltCount} bezahlt`}
          href="/anmeldungen"
          gradient="gradient-card-rose bg-card"
          iconColor="bg-chart-3/15 text-chart-3"
          icon={<ClipboardList size={20} />}
        />
      </div>

      {/* Charts + Recent row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Anmeldungen pro Monat */}
        <div className="lg:col-span-2 bg-card rounded-2xl border border-border/60 shadow-card p-6">
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp size={16} className="text-primary" />
            <h2 className="text-sm font-semibold tracking-wide text-foreground">Anmeldungen der letzten 6 Monate</h2>
          </div>
          {loading ? (
            <div className="h-48 flex items-center justify-center text-muted-foreground text-sm">Lädt…</div>
          ) : (
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={monthlyData} barSize={28}>
                <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.9 0.01 240)" vertical={false} />
                <XAxis dataKey="monat" tick={{ fontSize: 12, fill: 'oklch(0.52 0.02 255)' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 12, fill: 'oklch(0.52 0.02 255)' }} axisLine={false} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ background: 'white', border: '1px solid oklch(0.9 0.01 240)', borderRadius: '10px', fontSize: '13px' }}
                  labelStyle={{ fontWeight: 600 }}
                  formatter={(v) => [v, 'Anmeldungen']}
                />
                <Bar dataKey="anmeldungen" fill="oklch(0.42 0.18 265)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Zahlungsstatus */}
        <div className="bg-card rounded-2xl border border-border/60 shadow-card p-6">
          <div className="flex items-center gap-2 mb-6">
            <Euro size={16} className="text-primary" />
            <h2 className="text-sm font-semibold tracking-wide text-foreground">Zahlungsstatus</h2>
          </div>
          {loading ? (
            <div className="h-48 flex items-center justify-center text-muted-foreground text-sm">Lädt…</div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 rounded-xl bg-chart-3/10 border border-chart-3/20">
                <div className="flex items-center gap-3">
                  <CheckCircle2 size={18} className="text-chart-3" />
                  <span className="text-sm font-medium">Bezahlt</span>
                </div>
                <span className="text-2xl font-bold tabular-nums">{bezahltCount}</span>
              </div>
              <div className="flex items-center justify-between p-4 rounded-xl bg-chart-5/10 border border-chart-5/20">
                <div className="flex items-center gap-3">
                  <Clock size={18} className="text-chart-5" />
                  <span className="text-sm font-medium">Ausstehend</span>
                </div>
                <span className="text-2xl font-bold tabular-nums">{offenCount}</span>
              </div>
              {anmeldungen.length > 0 && (
                <div className="mt-4">
                  <div className="flex justify-between text-xs text-muted-foreground mb-1.5">
                    <span>Bezahlt</span>
                    <span>{Math.round((bezahltCount / anmeldungen.length) * 100)}%</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-chart-3 rounded-full transition-smooth"
                      style={{ width: `${(bezahltCount / anmeldungen.length) * 100}%` }}
                    />
                  </div>
                </div>
              )}
              <div className="pt-2 border-t border-border">
                <p className="text-xs text-muted-foreground">Gesamteinnahmen</p>
                <p className="text-xl font-bold mt-0.5">
                  {gesamtEinnahmen.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Recent Anmeldungen */}
      {recentAnmeldungen.length > 0 && (
        <div className="bg-card rounded-2xl border border-border/60 shadow-card p-6">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2">
              <ClipboardList size={16} className="text-primary" />
              <h2 className="text-sm font-semibold tracking-wide">Neueste Anmeldungen</h2>
            </div>
            <Link to="/anmeldungen" className="text-xs text-primary font-medium hover:underline">
              Alle anzeigen →
            </Link>
          </div>
          <div className="space-y-2">
            {recentAnmeldungen.map(a => (
              <div key={a.record_id} className="flex items-center justify-between py-3 border-b border-border/50 last:border-0">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-xs font-semibold text-primary">
                      {getTeilnehmerName(a.fields.teilnehmer).charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm font-medium">{getTeilnehmerName(a.fields.teilnehmer)}</p>
                    <p className="text-xs text-muted-foreground">{getKursTitle(a.fields.kurs)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {a.fields.anmeldedatum && (
                    <span className="text-xs text-muted-foreground">
                      {format(parseISO(a.fields.anmeldedatum), 'dd.MM.yyyy')}
                    </span>
                  )}
                  <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    a.fields.bezahlt
                      ? 'bg-chart-3/12 text-chart-3'
                      : 'bg-chart-5/12 text-chart-5'
                  }`}>
                    {a.fields.bezahlt ? 'Bezahlt' : 'Offen'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
