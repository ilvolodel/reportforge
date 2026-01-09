# 🔧 Micro-Agent Maintenance Guide

> **Come mantenere aggiornata la documentazione del progetto**

---

## 📋 Documenti da Mantenere

### 1. **PROJECT_STATE.md** (Principale) 🎯
**Quando aggiornare:**
- ✅ Dopo ogni milestone completata
- ✅ Quando cambia l'infrastruttura (nuovi server, domini, credenziali)
- ✅ Quando si aggiungono/modificano tabelle del database
- ✅ Quando si aggiungono nuovi API endpoints
- ✅ Quando si risolvono problemi critici (aggiornare "Known Issues")
- ✅ Fine settimana/sprint (review generale)

**Cosa aggiornare:**
```markdown
## Sezioni da verificare ogni volta:

□ **Last Updated** - Data in alto
□ **Version** - Incrementare quando si completa un task importante
□ **Status** - 🟢/🟡/🔴 badge
□ **Current Development Status** - Task completati vs in progress
□ **Database Schema** - Se sono state aggiunte/modificate tabelle
□ **API Endpoints** - Se sono stati aggiunti nuovi endpoint
□ **Known Issues** - Marcare come resolved o aggiungere nuovi
□ **Next Steps** - Aggiornare le priorità
```

### 2. **Task Tracker** (In-Session) ⏱️
**Quando aggiornare:**
- ✅ All'inizio di ogni sessione (view per vedere stato)
- ✅ Quando si completa un task (segnare come done)
- ✅ Quando si scopre nuovo lavoro necessario (aggiungere task)
- ✅ Quando si cambia priorità

**Come usare:**
```bash
# Vedere stato attuale
task_tracker view

# Aggiornare quando completi qualcosa
task_tracker plan [...]  # Con task marked as "done"

# Aggiungere nuovi task scoperti durante lo sviluppo
task_tracker plan [...]  # Con nuovi task aggiunti
```

### 3. **Guide Specifiche** 📚
**Quando creare/aggiornare:**
- ✅ Quando cambia una procedura (es. deploy, migration)
- ✅ Quando si aggiunge una nuova feature complessa
- ✅ Quando si risolve un problema che potrebbe ripresentarsi

**Esempi:**
- `MIGRATION_INSTRUCTIONS.md` - Quando cambiano procedure di migrazione DB
- `DEPLOYMENT_GUIDE.md` - Quando cambia il processo di deploy
- `API_DOCUMENTATION.md` - Quando si aggiungono molti nuovi endpoint

---

## 🔄 Workflow di Aggiornamento

### **Ogni Task Completato** (2 minuti)

```bash
# 1. Aggiorna task tracker
task_tracker plan [...]  # Mark task as done

# 2. Commit codice con messaggio descrittivo
git add -A
git commit -m "feat: description of what was done"
git push

# 3. Se è un task importante, aggiorna PROJECT_STATE.md
# (Solo le sezioni rilevanti, non tutto)
```

### **Fine Sprint/Settimana** (10-15 minuti)

```bash
# 1. Review completa di PROJECT_STATE.md
# - Update date e version
# - Current Development Status
# - Completed tasks list
# - Next Steps priorities

# 2. Cleanup eventuali guide obsolete

# 3. Commit delle modifiche
git add PROJECT_STATE.md
git commit -m "docs: Update project state - Sprint X complete"
git push
```

### **Cambi Infrastrutturali** (5 minuti)

```bash
# Se cambiano: domini, server, credenziali, stack tecnologico

# 1. Aggiorna sezione Infrastructure di PROJECT_STATE.md
# 2. Aggiorna eventuali script di deploy
# 3. Testa che tutto funzioni
# 4. Commit
```

### **Nuove Feature/API** (3-5 minuti)

```bash
# Quando aggiungi nuovi endpoint o modelli

# 1. Aggiorna sezione "API Endpoints" in PROJECT_STATE.md
# 2. Aggiorna sezione "Database Schema" se pertinente
# 3. Aggiungi esempi di utilizzo
# 4. Commit
```

---

## 📊 Template per Update Rapido

### Quick Update Checklist

Copia questo quando fai un update di PROJECT_STATE.md:

```markdown
## Update Checklist - [DATA]

**Versione:** 0.X.0 → 0.Y.0
**Sprint/Milestone:** [nome]

### ✅ Completato in questo update:
- [ ] Task X: [descrizione]
- [ ] Task Y: [descrizione]
- [ ] Bug fix: [descrizione]

### 📝 Modifiche alla documentazione:
- [ ] Aggiornato "Last Updated" e "Version"
- [ ] Aggiornato "Current Development Status"
- [ ] Aggiornato "Database Schema" (se applicabile)
- [ ] Aggiornato "API Endpoints" (se applicabile)
- [ ] Aggiornato "Known Issues" (risolti o nuovi)
- [ ] Aggiornato "Next Steps"

### 🔄 Deployment:
- [ ] Codice committato e pushato
- [ ] Deploy eseguito (se necessario)
- [ ] Verificato in produzione

### 📋 Note aggiuntive:
[Qualsiasi informazione importante da ricordare]
```

---

## 🎯 Sezioni PROJECT_STATE.md - Guida Rapida

### Quando aggiornare ogni sezione:

| Sezione | Quando Aggiornare | Frequenza |
|---------|------------------|-----------|
| **Last Updated** | Ogni modifica a PROJECT_STATE.md | Sempre |
| **Version** | Task milestone completata | Ogni 2-3 task |
| **Status Badge** | Cambi importanti nello stato | Quando cambia fase |
| **Project Overview** | Cambio requisiti o scope | Raro |
| **Infrastructure** | Nuovi server, domini, credenziali | Quando cambia infra |
| **Technology Stack** | Nuove librerie/framework importanti | Quando aggiungi tech |
| **Database Schema** | Nuove tabelle o campi significativi | Ogni modifica DB |
| **API Endpoints** | Nuovi endpoint o cambi importanti | Ogni nuovo API |
| **Current Development Status** | Completamento task | Ogni task done |
| **Common Operations** | Nuove procedure o cambi a esistenti | Quando cambiano |
| **Known Issues** | Nuovi problemi o risoluzioni | Quando si verificano |
| **Next Steps** | Cambio priorità o nuovi task scoperti | Settimanale |

---

## 🚀 Best Practices

### ✅ DO:

1. **Aggiorna subito dopo cambi importanti** - Non aspettare troppo o dimenticherai dettagli
2. **Usa commit descrittivi** - Es: "docs: Update PROJECT_STATE after Reports API completion"
3. **Mantieni consistenza** - Usa gli stessi termini/nomi in tutta la documentazione
4. **Documenta decisioni importanti** - Perché hai scelto approccio X invece di Y
5. **Aggiorna "Known Issues" quando risolvi** - Aiuta a non rifare gli stessi errori
6. **Testa prima di documentare** - Verifica che le procedure funzionino davvero

### ❌ DON'T:

1. **Non creare documenti duplicati** - Un solo PROJECT_STATE.md, non versioni multiple
2. **Non dimenticare la data** - Senza "Last Updated" non sai se è attuale
3. **Non documentare troppo in dettaglio** - Codice che cambia spesso va commentato nel codice, non qui
4. **Non lasciare task "in_progress" troppo a lungo** - O sono done o sono blocked
5. **Non scrivere guide senza esempi** - Aggiungi sempre comandi/codice esemplificativo
6. **Non ignorare problemi noti** - Se c'è un bug/issue, documentalo anche se non hai soluzione

---

## 🔍 Come Verificare se la Doc è Aggiornata

### Quick Check (30 secondi):

```bash
# 1. Controlla data "Last Updated"
head -20 PROJECT_STATE.md | grep "Last Updated"

# 2. Confronta con ultima modifica del codice
git log -1 --format="%ai" backend/

# 3. Se la differenza è > 1 giorno, probabilmente va aggiornato
```

### Deep Check (5 minuti):

```markdown
□ La sezione "Current Development Status" riflette lo stato reale?
□ Tutti i task completati sono marcati come done?
□ Le API documentate corrispondono a quelle nel codice?
□ Lo schema DB corrisponde ai modelli attuali?
□ I "Next Steps" sono ancora validi e prioritizzati correttamente?
□ I "Known Issues" sono attuali? (risolti = segnare come resolved)
```

---

## 📝 Esempio Pratico di Update

### Scenario: Hai appena completato il Task 27 (PDF Template)

**Step 1: Aggiorna PROJECT_STATE.md**

```markdown
## Cosa modificare:

1. Header:
   > **Last Updated:** 2026-01-10 [cambia data]
   > **Version:** 0.4.0 [incrementa]

2. Current Development Status:
   ### ✅ Completed (Tasks 1-27) [aggiungi 27]
   27. **HTML/CSS Modular PDF Template**
       - Created base template with InfoCert branding ✅
       - Implemented modular sections (show/hide) ✅
       - WeasyPrint-compatible CSS ✅

3. Known Issues:
   [Se hai trovato problemi durante lo sviluppo, aggiungili qui]

4. Next Steps:
   ### Immediate (Current Sprint)
   1. **Implement PDF Generation** [questo diventa priorità #1]
```

**Step 2: Commit**

```bash
git add PROJECT_STATE.md
git commit -m "docs: Update PROJECT_STATE after Task 27 completion

- Marked PDF template as complete
- Updated version to 0.4.0
- Updated next steps priorities"
git push
```

---

## 🎓 Pro Tips

### 1. **Usa Search & Replace** per consistenza

```bash
# Cerca tutti i riferimenti a una feature per essere sicuro di aggiornarli tutti
grep -r "Reports API" PROJECT_STATE.md
```

### 2. **Template di Commit per Docs**

```
docs: [tipo] - [descrizione breve]

[Dettagli delle modifiche]

Sections updated:
- [Sezione 1]
- [Sezione 2]
```

Esempi:
- `docs: update PROJECT_STATE after Task X completion`
- `docs: add MIGRATION_INSTRUCTIONS for new feature`
- `docs: fix outdated API endpoints documentation`

### 3. **Crea Snapshot Backup**

Prima di un grande refactoring:
```bash
cp PROJECT_STATE.md PROJECT_STATE_backup_$(date +%Y%m%d).md
# Fai modifiche
# Se va male, ripristina dal backup
```

### 4. **Link Incrociati**

Quando crei nuove guide, linkale in PROJECT_STATE.md:
```markdown
## Additional Documentation

- [Migration Instructions](./MIGRATION_INSTRUCTIONS.md) - Database migration procedures
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Production deployment workflow
- [API Documentation](./API_DOCUMENTATION.md) - Complete API reference
```

---

## 📊 Metriche di "Salute" della Documentazione

### 🟢 Documentazione Sana:
- ✅ Last Updated < 7 giorni fa
- ✅ Tutti i task completati sono marcati done
- ✅ API docs corrispondono al codice
- ✅ Known Issues sono attuali
- ✅ Next Steps sono chiari e prioritizzati

### 🟡 Documentazione da Aggiornare:
- ⚠️ Last Updated 7-14 giorni fa
- ⚠️ Alcuni task completati non marcati
- ⚠️ API docs mancano alcuni endpoint
- ⚠️ Known Issues potrebbero essere outdated

### 🔴 Documentazione Obsoleta:
- ❌ Last Updated > 14 giorni fa
- ❌ Status non riflette la realtà
- ❌ API docs significativamente diversi dal codice
- ❌ Known Issues non verificati

---

## 🎯 TL;DR - Azioni Minime Necessarie

### Ogni Giorno di Sviluppo:
1. ✅ Aggiorna task tracker quando completi task
2. ✅ Commit codice con messaggi descrittivi

### Ogni Task Importante Completato:
1. ✅ Aggiorna "Current Development Status" in PROJECT_STATE.md
2. ✅ Aggiorna sezioni specifiche se pertinente (API, DB, etc.)
3. ✅ Commit con messaggio "docs: update after Task X"

### Ogni Settimana/Sprint:
1. ✅ Review completa di PROJECT_STATE.md
2. ✅ Update di Last Updated, Version, Next Steps
3. ✅ Cleanup Known Issues (mark resolved)

### Ad Ogni Cambiamento Infrastrutturale:
1. ✅ Aggiorna Infrastructure section
2. ✅ Testa che tutto funzioni
3. ✅ Documenta eventuali gotcha

---

**Ricorda:** La documentazione è utile solo se è aggiornata! 🎯

Meglio un update piccolo e frequente che uno grande e mai fatto.
