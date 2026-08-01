# Sources

Original reference material — PDFs, books, course files, notes — that
Guardian's knowledge is built from. This directory is local-only, is not
committed to git (`.gitignore` excludes everything here except this file:
one of these files alone is over 100MB, and licensing on this material
varies), and is never read directly by `guardian_core`. It exists purely to
be analyzed into `extraction/` documents, which is where the authoring
workflow actually starts.

```
sources/<domain>/<file>                                  (this directory — local, untracked, raw)
      ↓  registration (this SOP)
knowledge/domains/source/sources/<slug>.yaml              (a Source entity — tracked, canonical)
      ↓  analysis (approved per-source, not automatic)
extraction/<domain>/<entity_type>/<slug>.md               (see extraction/README.md)
      ↓  review
knowledge/domains/<domain>/<entity_type>s/<slug>.yaml
      ↓  build_corpus() validation → Knowledge Package → guardian_core
```

## Standard operating procedure: registering new source documents

This is the standing process for whenever a file is added to or changed in
this directory. It is a procedure to run on request (e.g. "check for new
sources"), not an automated hook — no script executes it unprompted.

1. **Scan.** List every file under `sources/`, and compute each one's
   SHA-256 content hash.
2. **Match against the registry.** A file is already registered if some
   `knowledge/domains/source/sources/*.yaml` has `data.reference_url` equal
   to this file's path relative to the repo root. A file is **modified** if
   it's already registered but its current hash doesn't match the hash
   recorded in that Source entity's `data.notes`.
3. **Register new files.** For each new (or modified) file, create/update a
   minimal `Source` entity:
   - `status: draft`
   - `provenance.confidence: unverified` (the default — nobody has yet
     verified the bibliographic details)
   - `data.source_type`: best-effort guess (usually `pdf`)
   - `data.reference_url`: the file's path relative to repo root
   - `data.author` / `data.publication_year` / `data.citation`: filled in
     only where stated in the document itself — never guessed or invented
   - `data.notes`: the SHA-256 hash (for future modified-file detection),
     plus a one-line description of what the file appears to contain
   - one `changelog` entry recording this as an automated intake, not a
     content review
   A modified file gets a new `changelog` entry and an updated hash in
   `notes`, on top of its existing entry — its registration is never
   silently overwritten.
4. **Stop.** Registering a Source entity never triggers extraction. No
   `extraction/` document is created as part of this step, regardless of
   how many new files were found.
5. **Report and wait.** Present the newly-registered (or updated) sources
   and wait for explicit approval on which one(s) to move forward on next.
6. **On approval, resume the standard pipeline** (documented in full in
   `extraction/README.md`): one approved source → one `extraction/`
   document → review → one canonical YAML entity → rebuilt Knowledge
   Package. Approval is granted per source, not blanket — registering ten
   files and approving one of them for extraction is the expected shape of
   this workflow, not an exception to it.
