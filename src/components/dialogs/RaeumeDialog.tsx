import { useState, useEffect } from 'react';
import type { Raeume } from '@/types/app';
import { APP_IDS } from '@/types/app';
import { extractRecordId, createRecordUrl } from '@/services/livingAppsService';
import {
  Dialog, DialogContent, DialogHeader,
  DialogTitle, DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface RaeumeDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (fields: Raeume['fields']) => Promise<void>;
  defaultValues?: Raeume['fields'];
}

export function RaeumeDialog({ open, onClose, onSubmit, defaultValues }: RaeumeDialogProps) {
  const [fields, setFields] = useState<Partial<Raeume['fields']>>({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (open) setFields(defaultValues ?? {});
  }, [open, defaultValues]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await onSubmit(fields as Raeume['fields']);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={v => !v && onClose()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{defaultValues ? 'Räume bearbeiten' : 'Räume hinzufügen'}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="raumname">Raumname *</Label>
            <Input
              id="raumname"
              value={fields.raumname ?? ''}
              onChange={e => setFields(f => ({ ...f, raumname: e.target.value }))}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="gebaeude">Gebäude</Label>
            <Input
              id="gebaeude"
              value={fields.gebaeude ?? ''}
              onChange={e => setFields(f => ({ ...f, gebaeude: e.target.value }))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="kapazitaet">Kapazität</Label>
            <Input
              id="kapazitaet"
              type="number"
              value={fields.kapazitaet ?? ''}
              onChange={e => setFields(f => ({ ...f, kapazitaet: e.target.value ? Number(e.target.value) : undefined }))}
            />
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