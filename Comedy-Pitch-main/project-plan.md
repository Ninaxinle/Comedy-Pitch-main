Below is a **single, fully-integrated plan** incorporating every revision you requested:

* mobile-only React front-end (wrapped in Capacitor)
* Python / FastAPI back-end (one back-end developer only)
* two dedicated data-scientists
* Product person codes **front-end only** and spends 1 h / week on PM duties
* Comments / Event Listing / Notifications stay **stretch goals** (pursued only if slack remains from Week 7 onward)

---

## 0 · Executive Summary

| Item                   | Detail                                                                                                                                                                                                                                                                                    |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Hackathon Window**   | **Mon 23 Jun → Sat 23 Aug 2025** (9 build weeks + demo week)                                                                                                                                                                                                                              |
| **Demo Goal**          | Live mobile web app (PWA + Capacitor shells) where comedians can upload a set and instantly see an **AI funniness score & line-by-line heat-map**; fans can browse, play, like, and search sets.                                                                                          |
| **Must-Have Features** | 1️⃣ Registration/Login (Firebase)  2️⃣ Comedian Profile  3️⃣ Upload (video→audio)  4️⃣ Playback  5️⃣ Feed/Explore  6️⃣ Likes  7️⃣ Comedian Dashboard w/ views + AI heat-map  8️⃣ Basic name/title Search  9️⃣ ML pipeline (ingest→ASR→laughter→score→line map)  🔟 Analytics Dashboard UI |
| **Stretch (W 7+)**     | Flat Comments → Event Listing → In-app Toast Notifications                                                                                                                                                                                                                                |

---

## 1 · Team & Weekly Capacity (effective hrs)

| Stream             | People                                             | Coding h/wk ea. | 9-wk Total | Notes                                    |
| ------------------ | -------------------------------------------------- | --------------: | ---------: | ---------------------------------------- |
| **DATA / ML**      | DS-A 5 h · DS-B 4 h                                |           **9** |     **81** | Pipeline, ASR, laughter, models          |
| **BACK-END**       | **System Architect** 6 h                           |           **6** |     **54** | Auth, S3, FastAPI, DB, search, endpoints |
| **FRONT-END / UX** | Designer 5 h · Product Coder 3 h · iOS dev ≤ 2 h\* |          **10** |     **90** | React (Tailwind + shadcn/ui), Cap shells |
| **Coordination**   | Product PM 1 h                                     |               1 |          9 | Stand-ups, board upkeep                  |

*Total effective capacity ≈ **235 h**. Must-have work ≈ 180 h → \~ 25 % buffer.*

---

## 2 · Tech Stack Snapshot

| Layer         | Choice                                                                                            |
| ------------- | ------------------------------------------------------------------------------------------------- |
| Repo & CI/CD  | GitHub mono-repo · GitHub Actions → Fly.io (demo/prod)                                            |
| Auth          | Firebase Auth SDK                                                                                 |
| Storage       | S3 (raw video/audio)                                                                              |
| Back-End      | Python 3.12 · FastAPI · asyncpg (Postgres)                                                        |
| ML            | Whisper large-v3 (ASR) · VGGish laughter detector · XGBoost baseline → SBERT+laugh features model |
| Front-End     | React 18 · Vite · Tailwind CSS · shadcn/ui · Zustand                                              |
| Wrapper       | Capacitor 5 (iOS & Android)                                                                       |
| Observability | Prometheus + Grafana · Sentry (FE & BE)                                                           |

---

## 3 · Architecture (bird’s-eye)

```
React PWA (mobile)  <--JWT-->  FastAPI Gateway  <--local gRPC-->  ML Inference Service
        |                                    |
        | presigned PUT (video)              |  Postgres (users, videos, likes, scores)
        |                                    |
    S3 (HLS)                               Lambda (ffmpeg: video → audio.wav)
```

---

## 4 · Feature Decomposition & Owners

| #  | Feature                               | FE                 | BE                   | ML          |
| -- | ------------------------------------- | ------------------ | -------------------- | ----------- |
| 1  | Firebase Registration/Login           | Designer           | Sys Arch             | —           |
| 2  | Comedian Profile Page                 | Product → Designer | Sys Arch             | —           |
| 3  | Upload (video → audio via Lambda)     | Product            | **Sys Arch**         | —           |
| 4  | HLS Playback                          | Designer → iOS dev | —                    | —           |
| 5  | Feed / Explore                        | Product            | Sys Arch             | —           |
| 6  | Likes                                 | Product            | Sys Arch             | —           |
| 7  | Comedian Dashboard (views + heat-map) | Designer           | Sys Arch             | ML scores   |
| 8  | Basic Search (name/title)             | Designer           | Sys Arch             | —           |
| 9  | Ingestion Pipeline                    | —                  | Sys Arch (S3+Lambda) | DS-A · DS-B |
| 16 | Automatic Speech Transcription        | —                  | —                    | DS-B        |
| 17 | Laughter Detection                    | —                  | —                    | DS-B        |
| 18 | Baseline + SBERT Funniness Model      | —                  | —                    | DS-A        |
| 19 | Line-by-Line Analysis                 | —                  | —                    | DS-B        |
| 20 | Scoring API (gRPC / REST)             | Front-end consumes | Sys Arch wraps       | ML produces |

*(Stretch Comments/Event/Notif all FE+BE; no ML)*

---

## 5 · Week-by-Week Plan (Must-Have)

| Week                | DATA / ML (DS-A/DS-B)                                              | BACK-END (Sys Arch)                                 | FRONT-END / UX (Designer + Product)    | Milestone                                 |
| ------------------- | ------------------------------------------------------------------ | --------------------------------------------------- | -------------------------------------- | ----------------------------------------- |
| **W1** 23–29 Jun    |                                                                    | Repo scaffold · Firebase Auth middleware            | Figma mocks · Auth & Profile screens   | Auth works; laugh POC logged              |
| **W2** 30 Jun–6 Jul |                                                                    | `POST /upload/presign` → S3 · Lambda(audio-extract) | Feed card list (mock) · bottom nav     | Upload test succeeds                      |
| **W3** 7–13 Jul     | Model architecture design begins · Data labeling script setup      | `/feed` & `/like` endpoints · DB schema             | HLS player · like toggle · profile bio | E2E upload→feed→like demo; model scoped   |
| **W4** 14–20 Jul    | Parallel: Label data + Design experiments                          | `/search` (ILIKE)                                   | Upload form w/ progress · search UI    | Mid-sprint demo                           |
| **W5** 21–27 Jul    | Finalize model design · Begin model **training** (w/ partial data) | gRPC ML service + health-check                      | Dashboard heat-map (real API)          | First training run; dashboard API wired   |
| **W6** 28 Jul–3 Aug | Model training and evluation                                       | Rate limiting · Prometheus metrics                  | UX polish · a11y sweep                 | Model freeze; end-to-end data→score works |
| **W7** 4–10 Aug     | Model training and evluation                                       | Load test · error pages                             | Capacitor shells (iOS/Android)         | Code freeze – 1                           |
| **W8** 11–17 Aug    | Model training and evluation                                       | Deploy prod env · backups                           | Cosmetic sweep · bug-bash              | Code freeze                               |
| **W9** 18–22 Aug    | Model training and evluation                                       | —                                                   | Dry-runs · demo video                  | Ready                                     |
| **23 Aug**          | **LIVE DEMO**                                                      |                                                     |                                        | 🎉                                        |

---

## 6 · Stretch Goal Trigger (Week 7+)

*Enter only if* backlog ≤ 5 P2 bugs by Mon 4 Aug.

| Feature             | Effort | FE       | BE       |
| ------------------- | -----: | -------- | -------- |
| Flat Comments       |    5 h | Product  | Sys Arch |
| Event Listing       |    5 h | Designer | Sys Arch |
| Toast Notifications |    3 h | Product  | Sys Arch |

---

## 7 · Acceptance Criteria

| Area        | Metric                                              |
| ----------- | --------------------------------------------------- |
| Upload      | ≤ 60 s from video PUT to ML job queued              |
| Playback    | HLS stalls < 3 % on 4 G throttling                  |
| Likes       | UI count updates < 500 ms (optimistic)              |
| ML Accuracy | Spearman ρ ≥ 0.70 on 100-clip test set              |
| Search      | Response ≤ 300 ms for 90 % queries                  |
| Security    | All endpoints JWT-protected; public GETs idempotent |

---

## 8 · Risks & Mitigation

| Risk                      | Mitigation                                               |
| ------------------------- | -------------------------------------------------------- |
| Single back-end dev       | Daily commits, simple API surface, 8 h buffer            |
| ASR noise                 | Weight laugh features more; manual 1 h validation sample |
| Mobile video upload speed | Cap demo videos 720p/50 MB; recommend Wi-Fi              |
| Beta feedback overwhelm   | Lock new feature freeze on 4 Aug; bug fixes only after   |

---

## 9 · Project Management Processes

* **Board:** GitHub Projects with columns *Backlog / In Dev / PR Review / Done*.
* **Meetings:**

  * Monday async Slack check-in (15 min) — Product posts blockers list.
  * Friday 30 min Zoom demo & smoke-test to keep FE-BE-ML integration tight.
* **PR policy:** at least one reviewer; CI lint + unit tests must pass.
* **Definition of Done:** code merged, deployed to dev, acceptance tests pass, docs snippet added.

---

## 10 · Demo-Day Deliverables

1. **Live mobile site** + Capacitor test flight / APK.
2. GitHub repo with README and one-command deploy script.
3. ML model card (data, metrics, limitations).
4. 90-sec screen-record walkthrough.
5. Slide deck (objective → architecture → demo → next steps).

---

### Ready to Execute

This plan satisfies every required feature, fits within the recalculated capacity after removing the Product coder from back-end duties, and preserves a healthy buffer for the inevitable surprises of a part-time hackathon.  Good luck — and have fun!
