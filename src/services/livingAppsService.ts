// AUTOMATICALLY GENERATED SERVICE
import { APP_IDS } from '@/types/app';
import type { Dozenten, Teilnehmer, Raeume, Kurse, Anmeldungen } from '@/types/app';

// Base Configuration
const API_BASE_URL = 'https://my.living-apps.de/rest';

// --- HELPER FUNCTIONS ---
export function extractRecordId(url: string | null | undefined): string | null {
  if (!url) return null;
  // Extrahiere die letzten 24 Hex-Zeichen mit Regex
  const match = url.match(/([a-f0-9]{24})$/i);
  return match ? match[1] : null;
}

export function createRecordUrl(appId: string, recordId: string): string {
  return `https://my.living-apps.de/rest/apps/${appId}/records/${recordId}`;
}

async function callApi(method: string, endpoint: string, data?: any) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',  // Nutze Session Cookies für Auth
    body: data ? JSON.stringify(data) : undefined
  });
  if (!response.ok) throw new Error(await response.text());
  // DELETE returns often empty body or simple status
  if (method === 'DELETE') return true;
  return response.json();
}

export class LivingAppsService {
  // --- DOZENTEN ---
  static async getDozenten(): Promise<Dozenten[]> {
    const data = await callApi('GET', `/apps/${APP_IDS.DOZENTEN}/records`);
    return Object.entries(data).map(([id, rec]: [string, any]) => ({
      record_id: id, ...rec
    }));
  }
  static async getDozentenEntry(id: string): Promise<Dozenten | undefined> {
    const data = await callApi('GET', `/apps/${APP_IDS.DOZENTEN}/records/${id}`);
    return { record_id: data.id, ...data };
  }
  static async createDozentenEntry(fields: Dozenten['fields']) {
    return callApi('POST', `/apps/${APP_IDS.DOZENTEN}/records`, { fields });
  }
  static async updateDozentenEntry(id: string, fields: Partial<Dozenten['fields']>) {
    return callApi('PATCH', `/apps/${APP_IDS.DOZENTEN}/records/${id}`, { fields });
  }
  static async deleteDozentenEntry(id: string) {
    return callApi('DELETE', `/apps/${APP_IDS.DOZENTEN}/records/${id}`);
  }

  // --- TEILNEHMER ---
  static async getTeilnehmer(): Promise<Teilnehmer[]> {
    const data = await callApi('GET', `/apps/${APP_IDS.TEILNEHMER}/records`);
    return Object.entries(data).map(([id, rec]: [string, any]) => ({
      record_id: id, ...rec
    }));
  }
  static async getTeilnehmerEntry(id: string): Promise<Teilnehmer | undefined> {
    const data = await callApi('GET', `/apps/${APP_IDS.TEILNEHMER}/records/${id}`);
    return { record_id: data.id, ...data };
  }
  static async createTeilnehmerEntry(fields: Teilnehmer['fields']) {
    return callApi('POST', `/apps/${APP_IDS.TEILNEHMER}/records`, { fields });
  }
  static async updateTeilnehmerEntry(id: string, fields: Partial<Teilnehmer['fields']>) {
    return callApi('PATCH', `/apps/${APP_IDS.TEILNEHMER}/records/${id}`, { fields });
  }
  static async deleteTeilnehmerEntry(id: string) {
    return callApi('DELETE', `/apps/${APP_IDS.TEILNEHMER}/records/${id}`);
  }

  // --- RAEUME ---
  static async getRaeume(): Promise<Raeume[]> {
    const data = await callApi('GET', `/apps/${APP_IDS.RAEUME}/records`);
    return Object.entries(data).map(([id, rec]: [string, any]) => ({
      record_id: id, ...rec
    }));
  }
  static async getRaeumeEntry(id: string): Promise<Raeume | undefined> {
    const data = await callApi('GET', `/apps/${APP_IDS.RAEUME}/records/${id}`);
    return { record_id: data.id, ...data };
  }
  static async createRaeumeEntry(fields: Raeume['fields']) {
    return callApi('POST', `/apps/${APP_IDS.RAEUME}/records`, { fields });
  }
  static async updateRaeumeEntry(id: string, fields: Partial<Raeume['fields']>) {
    return callApi('PATCH', `/apps/${APP_IDS.RAEUME}/records/${id}`, { fields });
  }
  static async deleteRaeumeEntry(id: string) {
    return callApi('DELETE', `/apps/${APP_IDS.RAEUME}/records/${id}`);
  }

  // --- KURSE ---
  static async getKurse(): Promise<Kurse[]> {
    const data = await callApi('GET', `/apps/${APP_IDS.KURSE}/records`);
    return Object.entries(data).map(([id, rec]: [string, any]) => ({
      record_id: id, ...rec
    }));
  }
  static async getKurseEntry(id: string): Promise<Kurse | undefined> {
    const data = await callApi('GET', `/apps/${APP_IDS.KURSE}/records/${id}`);
    return { record_id: data.id, ...data };
  }
  static async createKurseEntry(fields: Kurse['fields']) {
    return callApi('POST', `/apps/${APP_IDS.KURSE}/records`, { fields });
  }
  static async updateKurseEntry(id: string, fields: Partial<Kurse['fields']>) {
    return callApi('PATCH', `/apps/${APP_IDS.KURSE}/records/${id}`, { fields });
  }
  static async deleteKurseEntry(id: string) {
    return callApi('DELETE', `/apps/${APP_IDS.KURSE}/records/${id}`);
  }

  // --- ANMELDUNGEN ---
  static async getAnmeldungen(): Promise<Anmeldungen[]> {
    const data = await callApi('GET', `/apps/${APP_IDS.ANMELDUNGEN}/records`);
    return Object.entries(data).map(([id, rec]: [string, any]) => ({
      record_id: id, ...rec
    }));
  }
  static async getAnmeldungenEntry(id: string): Promise<Anmeldungen | undefined> {
    const data = await callApi('GET', `/apps/${APP_IDS.ANMELDUNGEN}/records/${id}`);
    return { record_id: data.id, ...data };
  }
  static async createAnmeldungenEntry(fields: Anmeldungen['fields']) {
    return callApi('POST', `/apps/${APP_IDS.ANMELDUNGEN}/records`, { fields });
  }
  static async updateAnmeldungenEntry(id: string, fields: Partial<Anmeldungen['fields']>) {
    return callApi('PATCH', `/apps/${APP_IDS.ANMELDUNGEN}/records/${id}`, { fields });
  }
  static async deleteAnmeldungenEntry(id: string) {
    return callApi('DELETE', `/apps/${APP_IDS.ANMELDUNGEN}/records/${id}`);
  }

}