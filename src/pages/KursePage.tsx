import { useState, useEffect } from 'react';
import { LivingAppsService, extractRecordId, createRecordUrl } from '@/services/livingAppsService';
import type { Kurse, Dozenten, Raeume } from '@/types/app';
import { APP_IDS } from '@/types/app';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table, TableBody, TableCell, TableHead,
  TableHeader, TableRow,
} from '@/components/ui/table';
import { Pencil, Trash2, Plus, Search } from 'lucide-react';
import { KurseDialog } from '@/components/dialogs/KurseDialog';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import { PageShell } from '@/components/PageShell';
import { format, parseISO } from 'date-fns';
import { de } from 'date-fns/locale';

function formatDate(d?: string) {
  if (!d) return '—';
  try { return format(parseISO(d), 'dd.MM.yyyy', { locale: de }); } catch { return d; }
}

export default function KursePage() {
  const [records, setRecords] = useState<Kurse[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState<Kurse | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Kurse | null>(null);
  const [dozentenList, setDozentenList] = useState<Dozenten[]>([]);
  const [raeumeList, setRaeumeList] = useState<Raeume[]>([]);

  useEffect(() => { loadData(); }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [mainData, dozentenData, raeumeData] = await Promise.all([
        LivingAppsService.getKurse(),
        LivingAppsService.getDozenten(),
        LivingAppsService.getRaeume(),
      ]);
      setRecords(mainData);
      setDozentenList(dozentenData);
      setRaeumeList(raeumeData);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(fields: Kurse['fields']) {
    await LivingAppsService.createKurseEntry(fields);
    await loadData();
    setDialogOpen(false);
  }

  async function handleUpdate(fields: Kurse['fields']) {
    if (!editingRecord) return;
    await LivingAppsService.updateKurseEntry(editingRecord.record_id, fields);
    await loadData();
    setEditingRecord(null);
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    await LivingAppsService.deleteKurseEntry(deleteTarget.record_id);
    setRecords(prev => prev.filter(r => r.record_id !== deleteTarget.record_id));
    setDeleteTarget(null);
  }

  function getDozentenDisplayName(url?: string) {
    if (!url) return '—';
    const id = extractRecordId(url);
    return dozentenList.find(r => r.record_id === id)?.fields.name ?? '—';
  }

  function getRaeumeDisplayName(url?: string) {
    if (!url) return '—';
    const id = extractRecordId(url);
    return raeumeList.find(r => r.record_id === id)?.fields.raumname ?? '—';
  }

  const filtered = records.filter(r => {
    if (!search) return true;
    const s = search.toLowerCase();
    return Object.values(r.fields).some(v =>
      String(v ?? '').toLowerCase().includes(s)
    );
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <PageShell
      title="Kurse"
      subtitle={`${records.length} Kurse im System`}
      action={
        <Button onClick={() => setDialogOpen(true)} className="shrink-0">
          <Plus className="h-4 w-4 mr-2" /> Hinzufügen
        </Button>
      }
    >
      <div className="relative w-full max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Kurse suchen..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>
      <div className="rounded-lg border bg-card overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Titel</TableHead>
              <TableHead>Beschreibung</TableHead>
              <TableHead>Startdatum</TableHead>
              <TableHead>Enddatum</TableHead>
              <TableHead>Max. Teilnehmer</TableHead>
              <TableHead>Preis (€)</TableHead>
              <TableHead>Dozent</TableHead>
              <TableHead>Raum</TableHead>
              <TableHead className="w-24">Aktionen</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map(record => (
              <TableRow key={record.record_id} className="hover:bg-muted/50 transition-colors">
                <TableCell className="font-medium">{record.fields.titel ?? '—'}</TableCell>
                <TableCell className="max-w-xs"><span className="truncate block">{record.fields.beschreibung ?? '—'}</span></TableCell>
                <TableCell className="text-muted-foreground">{formatDate(record.fields.startdatum)}</TableCell>
                <TableCell className="text-muted-foreground">{formatDate(record.fields.enddatum)}</TableCell>
                <TableCell>{record.fields.max_teilnehmer ?? '—'}</TableCell>
                <TableCell>{record.fields.preis ?? '—'}</TableCell>
                <TableCell>{getDozentenDisplayName(record.fields.dozent)}</TableCell>
                <TableCell>{getRaeumeDisplayName(record.fields.raum)}</TableCell>
                <TableCell>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" onClick={() => setEditingRecord(record)}>
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(record)}>
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
            {filtered.length === 0 && (
              <TableRow>
                <TableCell colSpan={9} className="text-center py-16 text-muted-foreground">
                  {search ? 'Keine Ergebnisse gefunden.' : 'Noch keine Kurse. Jetzt hinzufügen!'}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <KurseDialog
        open={dialogOpen || !!editingRecord}
        onClose={() => { setDialogOpen(false); setEditingRecord(null); }}
        onSubmit={editingRecord ? handleUpdate : handleCreate}
        defaultValues={editingRecord?.fields}
        dozentenList={dozentenList}
        raeumeList={raeumeList}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Kurse löschen"
        description="Soll dieser Eintrag wirklich gelöscht werden? Diese Aktion kann nicht rückgängig gemacht werden."
      />
    </PageShell>
  );
}