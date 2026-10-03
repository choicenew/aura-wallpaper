# PyroPub - Mobile Apps Build, CI/CD, AI Search & Global SEO Distribution Hub

> **Official repository for build automation, release workflows, Google Play Store listing synchronization, AI agent indexing (`llms.txt`), and multi-search engine distribution of Pyro Studio applications.**

---

## 📢 Global Internal Beta Testing / 诚邀参与内测

Help us test our new Android utility! Similar to **LiveBridge**, it brings pickup codes, transit tickets, and parcel updates directly to your status bar island / capsule, and lets you transform ordinary notifications into real-time Live Updates!

### 🚀 How to Join (Participation Steps):

1. **Step 1 - Get Access Rights / 先进群组拿测试权限:**  
   👉 [Join Pyro Google Group](https://groups.google.com/g/pyroapp/members)
2. **Step 2 - Download via Google Play / 再点 Play 链接下载:**  
   👉 [Google Play Beta Testing Link (com.mypyro.veherego)](https://play.google.com/apps/testing/com.mypyro.veherego)

<details>
<summary><b>🇨🇳 中文内测招募说明 (Click to expand / 点击展开)</b></summary>

求各位大佬帮忙内测个安卓小工具：类似于 **LiveBridge**，能把取件码、车票等通知直接推上灵动岛/胶囊，并支持把系统普通通知自定义转成 Live Updates 实时动态。

**参与步骤：**
1. 先进群组拿测试权限：[Google Group 权限申请](https://groups.google.com/g/pyroapp/members)
2. 再点 Play 链接下载：[Google Play 内测下载 (com.mypyro.veherego)](https://play.google.com/apps/testing/com.mypyro.veherego)
</details>

---

## 📱 Global Multi-Language SEO Landing Page Suite & AI Search Standards

This repository manages four flagship Android applications, complete with automated CI/CD pipelines, IndexNow protocol pings, AI agent standard `llms.txt`, and 11-language global SEO landing pages:

| Application / Landing Page | Primary Target Audience & Niche | Landing & SEO Page | Privacy Policy | Google Play Package |
| :--- | :--- | :--- | :--- | :--- |
| **All-in-One App Hub** | Central Ecosystem Navigation Directory for All Apps | [App Navigation Portal](./nav/index.html) | - | Ecosystem Hub |
| **VehereGo** | Live Activity Hub, Status Bar Island, Parcel Pickup OCR, PKPass | [VehereGo SEO Landing](./veherego/index.html) | [Privacy Policy](./veherego/privacy.html) | `com.mypyro.veherego` |
| **PyroMagma Academic** | AI Academic Reader, Paper RAG Q&A, Edge LLM Digest, Zotero Sync | [PyroMagma Academic SEO](./pyromagma/index.html) | [Privacy Policy](./pyromagma/privacy.html) | `com.mypyro.pyromagma` |
| **PyroMagma Reader** | Legado Alternative, Free Novel/Manga Reader, Local AI OCR & Translation | [Legado Reader SEO Landing](./pyromagma/reader.html) | [Privacy Policy](./pyromagma/privacy.html) | `com.mypyro.pyromagma` |
| **YourCallYourRule** | Smart Call & SMS Blocker, Blacklist/Whitelist, Regex Rules, Plugins | [YourCallYourRule SEO](./yourcallyourrule/index.html) | - | `com.yours.yourcallyourrule` |

---

## 🤖 AI Search Engines (`llms.txt`) & Multi-Search Engine Protocol

All landing pages are equipped with active indexing hooks and instant submission protocols for **ChatGPT Search, Perplexity AI, Claude, Gemini, Google, Baidu, Bing, Yandex, DuckDuckGo, Naver, and Doubao**:

- **AI Search Engine Index Standard (`llmstxt.org`):** [`llms.txt`](./llms.txt) | Full Doc: [`llms-full.txt`](./llms-full.txt)
- **XML Sitemap (11 Languages with `hreflang`):** [`sitemap.xml`](./sitemap.xml)
- **Robots Directives (AI Crawlers & Search Spiders Allowed):** [`robots.txt`](./robots.txt)
- **IndexNow Instant Indexing Protocol:** Integrated into all HTML landing pages targeting `api.indexnow.org` for instant sub-second indexing on Bing, Yandex, DuckDuckGo, Naver, and Seznam.
- **Baidu LinkSubmit Auto-Push:** Client-side `push.js` automatically submits visited URLs directly to Baidu's indexing queue.
- **Google & Bing Sitemap Ping Triggers:** Client-side `navigator.sendBeacon` triggers sitemap pings on page load.

---

## 🌐 Multilingual Feature Overview (11 Target Languages)

Supported Languages: **English (EN), Simplified Chinese (ZH-CN), Traditional Chinese (ZH-TW), Japanese (JA), Korean (KO), Spanish (ES), German (DE), French (FR), Portuguese (PT), Russian (RU), Arabic (AR)**.

### 1. VehereGo: Live Activity & Parcel Hub
- **Status Bar Island & Capsules (灵动岛/胶囊通知):** Push real-time parcel updates, food delivery, flight/train status, and custom notifications to your status bar island.
- **Smart Pickup Code OCR & SMS Extraction (取件码识别与提取):** Auto-extract parcel pickup codes (Cainiao, SF Express, Hive Box, Meituan, etc.) from screenshots or SMS, generating instant barcodes/QRs.
- **PKPass Wallet (PKPass 数字卡包):** Native support for `.pkpass` digital passes, tickets, and membership cards.
- **Universal Calendar & Course Schedule (万年历与智能课程表):** Solar/Lunar almanac, 24 solar terms, odd/even week course schedules, and ICS calendar sync.
- **100% On-Device Local Processing (纯本地隐私保护):** Zero accounts required, 100% local processing, zero data uploads.

### 2. PyroMagma: AI Academic & Reader Engine
- **Legado (开源阅读) Alternative:** Supports custom book sources, EPUB, PDF, RSS, and web novels without ads.
- **On-Device Local AI Translation:** Translate raw Japanese/English web novels offline with zero API cost or latency.
- **Real-Time Manga Speech Bubble OCR:** Extract text from comic panels instantly for side-by-side translation.
- **Free Academic Paper Reader & RAG:** Access ArXiv, IEEE, Nature, and Science papers with interactive AI Q&A over complex formulas.
- **Multi-Cloud Reference Sync:** Seamless 1-click sync with Zotero, EndNote, Mendeley, and WebDAV.

### 3. YourCallYourRule: Smart Call & SMS Blocker
- **Blacklist & Whitelist Management:** Block unwanted callers, spam numbers, telemarketers, and robocalls.
- **Regular Expression Filtering:** Complex blocking rules for area codes, prefix patterns, and SMS keywords.
- **QuickJS Web Scraping Plugin System:** Scraping engine for identifying unknown caller IDs from web databases with QuickJS unit test runner.
- **STIR/SHAKEN Verification & WebDAV Backup:** Cryptographic caller ID validation and WebDAV/Google Drive cloud backup.

---

## ⚙️ Automated CI/CD Pipelines

- `.github/workflows/veherego_*.yml` - Build and release workflows for VehereGo (AAB, APK, Play Store release, Telegram deployment).
- `.github/workflows/pyromagma_*.yml` - Build and release workflows for PyroMagma.
- `.github/workflows/*_update_store_list.yml` - Synchronize multi-language Play Store titles, short descriptions, and full descriptions using `update-store-list/update.js`.

---

## 📧 Contact & Support

- **Developer:** Pyro Studio / ChoiceNew / oakgeol
- **Contact Email:** `OAKGEOL@GMAIL.COM`
- **Google Group:** [Pyro App Community](https://groups.google.com/g/pyroapp/members)
- **Telegram Channel:** [YourCallYourRule Telegram](https://t.me/yourcallyourrule)
