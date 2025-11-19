EUHealth tools: find and explore EU public-health datasets
=========================================================

Use these tools to:

* **Search** public EU health datasets by topic (e.g., cancer, vaccination, obesity, mental health…)
* **Deep-dive** a dataset’s landing page to surface useful outgoing links (download portals, etc.)

You do **not** need to know about embeddings, dimensions, or FAISS. Everything is handled automatically.
All you need is a Hugging Face token (for downloading or uploading); ToolUniverse handles embedding models, caching, and FAISS indexing under the hood.

The tools read from a local library (a small database + index)::

<user_cache_dir>/embeddings/euhealth.db
<user_cache_dir>/embeddings/euhealth.faiss

---

Quick start (recommended): use the prebuilt library
---------------------------------------------------

1. **Get a Hugging Face token** (free account).
   Copy it once (Settings → Access Tokens).

2. **Download the ready-to-use EUHealth library:**

.. code-block:: bash

# download from your own or any public Hugging Face repo

export HF_TOKEN=YOUR_HF_TOKEN
tu-datastore sync-hf download 
--repo "agenticx/tooluniverse-datastores"
--collection euhealth 
--overwrite

That’s it — the files land in `<user_cache_dir>/embeddings/` where the tools expect them.

Don’t have a token or prefer not to make an account?
Skip to “Build it yourself” below.

Tip:
If you previously uploaded your own copy of the EUHealth datastore (`tu-datastore sync-hf upload --collection euhealth`),
it lives at `huggingface.co/<your_username>/euhealth`.

---

Use it
------

Just talk to your agent in plain English. Examples:

* “**Find cancer datasets for Germany**.”
  → The agent uses the *euhealth cancer search* tool and returns a list.

* “**Show vaccination datasets in English**.”
  → The agent calls the vaccination topic tool with a language filter.

* “**Deep-dive the first 3 results and give me the best download links**.”
  → The agent calls the deep-dive tool to classify links from each dataset’s landing page (e.g., `html_portal`, `login_or_error`, etc.).

Behind the scenes, the agent uses the tools defined in
`src/tooluniverse/data/euhealth_tools.json`
(20 topics are pre-wired; you don’t have to touch this).

---

How search methods are chosen
-----------------------------------

The public tools accept ``method="keyword"|"embedding"|"hybrid"`` (default ``"hybrid"``).

* If your local EUHealth library is the **shared/official build** (embedded with
  ``text-embedding-3-small``), then:
  
  - ``embedding``/``hybrid`` are **allowed** only when the caller resolves to **Azure + text-embedding-3-small**. (e.g. AZURE_OPENAI_DEPLOYMENT=text-embedding-3-small, EMBED_PROVIDER=azure)
  - Otherwise, we **silently fall back to** ``"keyword"`` (so tools still work without errors).

* If you **built the library yourself** (any provider/model), the requested method is honored
  (no fallback).

This guarantees the prebuilt library “just works” everywhere, while advanced users still get full embedding/hybrid behavior with their own builds.

---

Optional: quick terminal “smoke test”
----------------------------------------

If you want to sanity-check from Terminal (no coding):

.. code-block:: bash

# Keyword search (works without any API keys)

tu-datastore search 
--collection euhealth 
--query cancer 
--method keyword 
--top-k 5

You should see a few JSON results (uuid, title, landing_page, etc.).
(Inside the agent you’ll get nicely formatted results. This is just a quick check.)

---

Build it yourself (only if you can’t use the prebuilt)
------------------------------------------------------

If you can’t download from Hugging Face, you can build locally. You’ll need any one of:

* **OpenAI** (simplest): `OPENAI_API_KEY`, `EMBED_PROVIDER=openai`, `EMBED_MODEL=text-embedding-3-small`
* **Azure OpenAI**: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `OPENAI_API_VERSION`
* **Hugging Face**: `HF_TOKEN`, `EMBED_PROVIDER=huggingface`, `EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2`

Then run:

.. code-block:: bash

# pick one provider, for example OpenAI:

export EMBED_PROVIDER=openai
export EMBED_MODEL=text-embedding-3-small
export OPENAI_API_KEY=YOUR_KEY

# build (crawl the portal, normalize, embed, index)

python -m tooluniverse.euhealth.euhealth_live

This writes the same two files to `<user_cache_dir>/embeddings/`.
Re-running is safe; it adds new items and skips duplicates.

You never need to specify an embedding dimension or configuration. ToolUniverse detects your provider and model automatically, using the same backend as `tu-datastore build`.

---

What each tool returns
----------------------

**Topic search tools** (e.g., cancer, vaccination, mental health) return a list of:

.. code-block:: json

   {
     "uuid": "…",
     "title": "…",
     "landing_page": "https://…",
     "license": "…",
     "keywords": ["…"],
     "themes": ["…"],
     "language": ["…"],
     "spatial": "…",
     "snippet": "first ~280 chars of text"
   }


**Deep-dive tool** (for selected datasets) returns:

.. code-block:: json

   {
     "uuid": "…",
     "title": "…",
     "landing_page": "…",
     "candidates": [
       {
         "url": "…",
         "classification": "html_portal | login_or_error | error",
         "http_status": 200,
         "content_type": "text/html",
         "notes": "…"
       }
     ]
   }

---

Common questions
-------------------

* **Do I need to configure anything in code?**
  No, the tools are already registered. If the library exists in `<user_cache_dir>/embeddings/`, you can just ask the agent.

* **Can I filter by country/language?**
  Yes, just say ask for it in your query (“Germany”, “DE”, “English”, “en”). The tools accept both plain names and codes.

* **What if some links say `login_or_error`?**
  Some portals require accounts or block automated requests. The tool still shows you what’s there.

* **My agent says the EUHealth library isn’t found.**
  Make sure the files exist at::

  <user_cache_dir>/embeddings/euhealth.db
  <user_cache_dir>/embeddings/euhealth.faiss

  If not, use the **Quick start** download or the **Build it yourself** step.

* **Where does my data upload now?**
  When you run `tu-datastore sync-hf upload --collection euhealth`, ToolUniverse automatically detects your `HF_TOKEN` and uploads to **your own Hugging Face namespace** (`your_username/euhealth`).
  The `--repo` flag is optional; if omitted, it defaults to `<your_username>/<collection>`.

---

(Optional, for maintainers) Keep it fresh weekly
------------------------------------------------

A scheduled GitHub Actions workflow automatically rebuilds and uploads the EUHealth datastore each week.

* Workflow file: `.github/workflows/euhealth-cache-refresh.yml`
* Schedule: Mondays at 06:00 UTC
* Steps performed:
  1. Run the live builder (`euhealth_live`) to refresh data and embeddings.
  2. Upload the new `euhealth.db` and `euhealth.faiss` to the shared Hugging Face dataset:
     `agenticx/tooluniverse-datastores`.
    
You’ll need secrets configured in GitHub (e.g., `OPENAI_API_KEY`, `HF_TOKEN`, etc.) for the job to run successfully.

Most users can ignore this section, it’s only to keep the public EUHealth dataset fresh.
---

You’re set
----------

* Prefer the **Quick start** download.
* Ask the agent normal questions (“Find cancer datasets in Germany”).
* Use **deep-dive** when you want the actual outgoing links.

If you later want the nitty-gritty (how we crawl, embed, index), see the developer notes in:
`src/tooluniverse/euhealth/*` and `src/tooluniverse/database_setup/*`.

.. note::

Want to build or share your **own** searchable dataset or tool (like EUHealth)?
See: `docs/tutorials/make_your_data_agent_searchable.rst`: the 3-minute guide to creating and publishing your own ToolUniverse datastore.