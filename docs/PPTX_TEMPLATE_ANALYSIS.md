# 📊 Analisi Template PPTX INFOCERT - AI Customer Support

**File**: `Gennaio 2026 - Monthly Report.pptx`  
**Data Analisi**: 2026-01-08  
**Dimensioni**: 9.8MB  
**Totale Slide**: 29

---

## 🎯 Struttura del Template

### Slide Overview

| # | Layout | Shapes | Contenuto | Tabelle | Grafici | Immagini |
|---|--------|--------|-----------|---------|---------|----------|
| 1 | Copertina 1 | 1 | Titolo principale | ❌ | ❌ | ❌ |
| 2 | Layout personalizzato 7 | 16 | **EXECUTIVE SUMMARY** | ❌ | ❌ | ❌ |
| 3 | Layout personalizzato 8 | 7 | Progetti chiave 2025 | ❌ | ❌ | ❌ |
| 4 | Layout personalizzato 9 | 21 | Stakeholder | ❌ | ❌ | ✅ |
| 5-7 | Layout personalizzato | 3-18 | CHATBOT ANALYZER | ❌ | ❌ | ✅ |
| 8-17 | Layout personalizzato | 3-26 | CHATBOT EVOLUTION | ❌ | ❌ | ✅ |
| 18-19 | Layout personalizzato | 3-15 | Migrazione infrastruttura | ❌ | ❌ | ✅ |
| 20 | Layout personalizzato | 3 | Sezione SALES | ❌ | ❌ | ❌ |
| 21 | Layout personalizzato | 47 | Trusty REVENUE & SAVING 2025 | ❌ | ❌ | ❌ |
| 22 | Layout personalizzato | 53 | Trusty Hub REVENUE 2026 | ❌ | ❌ | ❌ |
| 23-28 | Layout personalizzato | 20-32 | Dettagli progetti clienti | ❌ | ❌ | ❌ |
| 29 | Copertina fondo | 1 | Slide finale | ❌ | ❌ | ❌ |

---

## 📋 Sezioni Principali

### 1. **EXECUTIVE SUMMARY** (Slide 2) ⭐ CHIAVE

**Struttura**:
- Titolo: "EXECUTIVE SUMMARY – AI CUSTOMER SUPPORT 25/26"
- Sottotitolo: "GenAIHUB"
- Descrizione narrativa (2 box)
- Tabella comparativa 2025 vs 2026:
  - YEAR: 2025 | 2026 (expected)
  - BENEFICI: Lista benefici qualitativi
  - FINANCIAL: Revenue AI + Saving AI
  - TOTAL: Somma totale (425K vs 2.6M€)
  - STAKEHOLDER: Lista dipartimenti

**Dati da mappare nel database**:
```python
# Tabella: report_executive_summary
{
    'year_current': 2025,
    'year_forecast': 2026,
    'revenue_current': 375000,
    'saving_current': 50000,
    'total_current': 425000,
    'revenue_forecast': 2000000,
    'saving_forecast': 600000,
    'total_forecast': 2600000,
    'benefits': ['Leadership AI avanzate', 'Riduzione rischio reputazionale', ...],
    'stakeholders': ['Customer Care', 'Marketing', 'Sales', ...]
}
```

---

### 2. **PROGETTI CHIAVE** (Slide 3-19)

**Categorie progetti**:
1. **CHATBOT ANALYZER** (Slide 5-7)
   - CLEARSIGHT
   - Continuous Improvement
   
2. **CHATBOT EVOLUTION** (Slide 8-17)
   - SERVICE GURU
   - TRUSTY VOICE (SPID)
   - TRUSTY SPID WhatsApp
   - Marketing Copilot
   - SERVICE CATALOG COPILOT
   - ASTERIX
   - TRUSTY HUB
   - Trusty Screen Cast

3. **MIGRAZIONE INFRASTRUTTURA** (Slide 18-19)
   - Cloud Infrastructure Migration

**Struttura tipica progetto**:
- Titolo progetto
- Descrizione
- Stakeholder
- Immagini/screenshot
- Timeline/milestone

**Mappatura database**:
```python
# Tabella: projects
{
    'name': 'SERVICE GURU',
    'category': 'CHATBOT EVOLUTION',
    'description': 'Strumento intelligente a supporto del Customer Care e Sales',
    'status': 'In Progress',
    'start_date': '2025-01-01'
}

# Tabella: project_stakeholders
# Collegamenti tra progetti e stakeholder
```

---

### 3. **DETTAGLI SALES** (Slide 20-28) ⭐ IMPORTANTE

**Slide 21: Trusty REVENUE & SAVING 2025**

Struttura:
- Header: "Trusty REVENUE & SAVING 2025"
- Total Saving 2025: 50K
- Lista clienti con:
  - Nome cliente (es. INFOCERT, ASL CUNEO, LENOVYS)
  - Nome progetto/contatto
  - Data (es. 09/2025)
  - Status/Note (es. "In attesa del KICK-OFF")
  - Revenue (es. 10K)
  - Saving

**Mappatura database**:
```python
# Tabella: clients
{
    'name': 'ASL CUNEO',
    'type': 'Cliente',
    'acquisition_date': '2025-09-01'
}

# Tabella: subscriptions (o revenue_one_time)
{
    'client_id': 123,
    'project_id': 456,
    'amount': 10000,
    'type': 'Revenue',
    'date': '2025-09-01',
    'status': 'In attesa del KICK-OFF'
}
```

**Slide 22: Trusty Hub REVENUE 2026**

Struttura:
- Header: "Trusty Hub Revenue & Saving 2026"
- Lista clienti con:
  - CLIENTE / PROGETTO
  - PARTNER (opzionale)
  - NOTE
  - ULTIMA DATA RILEVANTE
  - REVENUE (es. 1.15 M€)

**Esempi clienti**:
- INFOCERT / NORMA (12/2025) - 1.15M€
- Altri clienti...

**Slide 23-28: Progetti in pipeline**

Struttura:
- Header con nome progetto/categoria
- Colonne:
  - CLIENTE
  - ATTIVITÀ
  - NOTE
  - ULTIMA DATA RILEVANTE
  - Capex (opzionale)

**Esempi**:
- ASST LECCO
- ASST NIGUARDA
- Altri prospect...

---

## 🔧 Pattern Identificati

### 1. **Layout Fisso**
- Tutte le slide usano layout personalizzati (7, 8, 9)
- Shapes con nomi specifici (Pentagono 31, Rettangolo arrotondato 63)
- Posizioni fisse per ogni elemento

### 2. **Nessuna Tabella PowerPoint**
- ❌ Le "tabelle" sono composte da shapes (rettangoli) disposti in griglia
- ✅ Più flessibilità ma più complessità nella generazione automatica

### 3. **Testo in Shapes**
- Tutti i dati sono text dentro AutoShapes
- Nomi shapes non parlanti (es. "Rettangolo arrotondato 63")
- Necessario identificare shapes per posizione o contenuto

### 4. **Immagini**
- 11 slide contengono immagini
- Probabilmente screenshot di interfacce/prodotti
- Posizionate manualmente

---

## 💡 Strategia di Automazione

### Opzione A: ⭐ CONSIGLIATA - Generazione PDF con WeasyPrint

**Vantaggi**:
- ✅ Layout più prevedibile e controllabile
- ✅ HTML/CSS più facile da mantenere
- ✅ Template Jinja2 per ogni sezione
- ✅ Perfetto per report formali
- ✅ Più veloce da implementare

**Workflow**:
1. Database → Query per estrarre dati
2. Template HTML/CSS per ogni sezione
3. Jinja2 per popolare template
4. WeasyPrint per generare PDF
5. Output: `Report_Gennaio_2026.pdf`

**Timeline**: ~5 giorni

---

### Opzione B: Generazione PPTX con python-pptx

**Vantaggi**:
- ✅ Riutilizzo template esistente
- ✅ Output modificabile
- ✅ Familiare per utenti abituati a PPTX

**Svantaggi**:
- ❌ Complessità: shapes senza nomi parlanti
- ❌ Layout basato su posizioni assolute
- ❌ Difficile identificare quale shape modificare
- ❌ Necessita LibreOffice per conversione PDF

**Workflow**:
1. Database → Query per estrarre dati
2. Carica template PPTX
3. **Problema**: Identificare shapes da modificare per posizione/indice
4. Sostituire testi in ogni shape
5. Salva nuovo PPTX
6. Opzionale: Converti in PDF con LibreOffice

**Timeline**: ~7-10 giorni (più complesso)

---

### Opzione C: Ibrida

**Workflow**:
1. Genera **PDF professionale** con WeasyPrint (per report formali)
2. **Opzionale**: Script di export dati in CSV per aggiornare PPTX manualmente

**Vantaggi**:
- ✅ Best of both worlds
- ✅ PDF automatico + flessibilità PPTX manuale

---

## 📊 Mappatura Database → Template

### Executive Summary (Slide 2)

```sql
-- Query per popolare Executive Summary
SELECT 
    year_current,
    year_forecast,
    revenue_current,
    saving_current,
    total_current,
    revenue_forecast,
    saving_forecast,
    total_forecast,
    benefits_text,
    stakeholders_text
FROM report_executive_summary
WHERE report_id = ?;
```

### Progetti (Slide 3-19)

```sql
-- Query per progetti
SELECT 
    p.name,
    p.category,
    p.description,
    p.status,
    GROUP_CONCAT(s.name) as stakeholders
FROM projects p
LEFT JOIN project_stakeholders ps ON p.id = ps.project_id
LEFT JOIN stakeholders s ON ps.stakeholder_id = s.id
WHERE p.report_id = ?
GROUP BY p.id
ORDER BY p.category, p.name;
```

### Sales & Revenue (Slide 21-28)

```sql
-- Query per revenue/saving 2025
SELECT 
    c.name as client_name,
    s.name as subscription_name,
    s.amount,
    s.type,
    s.status,
    s.start_date,
    s.notes
FROM subscriptions s
JOIN clients c ON s.client_id = c.id
WHERE s.year = 2025
ORDER BY s.start_date;

-- Query per revenue 2026
SELECT 
    c.name as client_name,
    p.name as project_name,
    r.amount,
    r.revenue_date,
    r.notes,
    r.partner_name
FROM revenue_one_time r
JOIN clients c ON r.client_id = c.id
LEFT JOIN projects p ON r.project_id = p.id
WHERE YEAR(r.revenue_date) = 2026
ORDER BY r.revenue_date;
```

---

## 🚀 Raccomandazione Finale

### ⭐ CONSIGLIO: Opzione A - PDF con WeasyPrint

**Motivi**:
1. Il template PPTX è **troppo complesso** per automatizzazione (shapes senza nomi, posizioni assolute)
2. **PDF è più professionale** per report mensili formali
3. **HTML/CSS molto più facile** da mantenere e modificare
4. **WeasyPrint già nel progetto** e funzionante
5. Layout fisso garantito al 100%
6. **Timeline più breve**: MVP in 5 giorni vs 10 giorni

### Template HTML Proposto

Creiamo template HTML/CSS che replica il design del PPTX:
- Stesso branding INFOCERT
- Stessi colori e font
- Layout simile ma più pulito
- Facile da aggiornare

**Il PPTX esistente serve come**:
- ✅ Reference per design/layout
- ✅ Guida per struttura contenuti
- ✅ Benchmark visuale

**Ma generiamo PDF, non PPTX!**

---

## 📝 Prossimi Passi

1. **✅ FATTO**: Analisi PPTX template
2. **TODO**: Creare template HTML/CSS basato su design PPTX
3. **TODO**: Implementare generatore PDF con WeasyPrint
4. **TODO**: Testare con dati reali Gennaio 2026
5. **TODO**: Deploy e validazione

---

**Sei d'accordo con questa strategia?** 🚀
