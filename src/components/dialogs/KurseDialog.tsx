import { useState, useEffect } from 'react';
import type { Kurse, Dozenten, Raeume } from '@/types/app';
import { APP_IDS } from '@/types/app';
import { extractRecordId, createRecordUrl } from '@/services/livingAppsService';
import {
  Dialog, DialogContent, DialogHeader,
  DialogTitle, DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select, SelectContent, SelectItem,
  SelectTrigger, SelectValue,
} from '@/components/ui/select';

interface KurseDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (fields: Kurse['fields']) => Promise<void>;
  defaultValues?: Kurse['fields'];
  dozentenList: Dozenten[];
  raeumeList: Raeume[];
}

export function KurseDialog({ open, onClose, onSubmit, defaultValues, dozentenList, raeumeList }: KurseDialogProps) {
  const [fields, setFields] = useState<Partial<Kurse['fields']>>({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (open) setFields(defaultValues ?? {});
  }, [open, defaultValues]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await onSubmit(fields as Kurse['fields']);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={v => !v && onClose()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{defaultValues ? 'Kurse bearbeiten' : 'Kurse hinzufügen'}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="titel">Titel *</Label>
            <Input
              id="titel"
              value={fields.titel ?? ''}
              onChange={e => setFields(f => ({ ...f, titel: e.target.value }))}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="beschreibung">Beschreibung</Label>
            <Textarea
              id="beschreibung"
              value={fields.beschreibung ?? ''}
              onChange={e => setFields(f => ({ ...f, beschreibung: e.target.value }))}
              rows={3}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="startdatum">Startdatum *</Label>
            <Input
              id="startdatum"
              type="date"
              value={fields.startdatum ?? ''}
              onChange={e => setFields(f => ({ ...f, startdatum: e.target.value }))}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="enddatum">Enddatum</Label>
            <Input
              id="enddatum"
              type="date"
              value={fields.enddatum ?? ''}
              onChange={e => setFields(f => ({ ...f, enddatum: e.target.value }))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="max_teilnehmer">Max. Teilnehmer</Label>
            <Input
              id="max_teilnehmer"
              type="number"
              value={fields.max_teilnehmer ?? ''}
              onChange={e => setFields(f => ({ ...f, max_teilnehmer: e.target.value ? Number(e.target.value) : undefined }))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="preis">Preis (€)</Label>
            <Input
              id="preis"
              type="number"
              value={fields.preis ?? ''}
              onChange={e => setFields(f => ({ ...f, preis: e.target.value ? Number(e.target.value) : undefined }))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="dozent">Dozent</Label>
            <Select
              value={extractRecordId(fields.dozent) ?? 'none'}
              onValueChange={v => setFields(f => ({ ...f, dozent: v === 'none' ? undefined : createRecordUrl(APP_IDS.DOZENTEN, v) }))}
            >
              <SelectTrigger id="dozent"><SelectValue placeholder="Auswählen..." /></SelectTrigger>
              <SelectContent>
                <SelectItem value="none">—</SelectItem>
                {dozentenList.map(r => (
                  <SelectItem key={r.record_id} value={r.record_id}>
                    {r.fields.name ?? r.record_id}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="raum">Raum</Label>
            <Select
              value={extractRecordId(fields.raum) ?? 'none'}
              onValueChange={v => setFields(f => ({ ...f, raum: v === 'none' ? undefined : createRecordUrl(APP_IDS.RAEUME, v) }))}
            >
              <SelectTrigger id="raum"><SelectValue placeholder="Auswählen..." /></SelectTrigger>
              <SelectContent>
                <SelectItem value="none">—</SelectItem>
                {raeumeList.map(r => (
                  <SelectItem key={r.record_id} value={r.record_id}>
                    {r.fields.raumname ?? r.record_id}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>Abbrechen</Button>
            <Button type="submit" disabled={saving}>
              {saving ? 'Speichern...' : defaultValues ? 'Speichern' : 'Erstellen'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}