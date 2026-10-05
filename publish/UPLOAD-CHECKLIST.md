# Upload checklist — ORCID, Zenodo DOI, Hugging Face

Steps only Tim can do: they create accounts, grant OAuth access, or publish under his name.
Everything else is already in the repository (`CITATION.cff`, `.zenodo.json`,
`publish/zenodo-paper.json`, `publish/huggingface/README.md`).

**Short path — about 35 minutes of Tim's time (decided 2026-10-05: Tim has < 5 h/week).**
Tim does only what needs his identity; Claude does the rest from the same machine:

| Tim | Claude, afterwards |
|---|---|
| §1 ORCID iD (10 min) and send the iD | §2 write it into the files |
| §3 Zenodo: log in with GitHub, switch the repo on (10 min) | §4 cut the release with `gh` (mints the DOI), §5 write the DOI back |
| §7 Hugging Face account + `hf auth login` with a write token, typed by Tim (15 min) | §8 create the dataset repo and upload, including sleep (§9) |
| §6 paper record: approve the filled form (optional, later) | §6 prepare the PDF and the form values |

The full manual path below stays as reference. Minutes are estimates; doing everything by hand
takes about **2 h 20 min**.

CLI syntax checked on 2026-10-05 against the Hugging Face CLI reference
(huggingface.co/docs/huggingface_hub/package_reference/cli). The old `huggingface-cli` command
was removed in `huggingface_hub` v1.0; use `hf`.

---

## 0. Before anything is published (15 min)

- [ ] **Sleep export landed?** `.zenodo.json` describes both categories. If `sleep/data/public/`
      is still empty at release time, either wait, or delete the sleep sentence from the
      `.zenodo.json` description first. (The Zenodo record is a frozen snapshot; a later fix
      means a new version.)
- [ ] **Two licence decisions** that the repository does not answer yet:
      - Code: `LICENSE` is the AGPL-3.0 text with no "or any later version" notice.
        `CITATION.cff` says `AGPL-3.0-only`. If you mean "or later", change it to
        `AGPL-3.0-or-later`.
      - Paper: no licence is stated for `docs/working-paper.md`. `publish/zenodo-paper.json`
        proposes `cc-by-4.0`. Confirm or change.
- [ ] **What goes into the archive.** Zenodo archives every tracked file in the release. That
      currently includes `openappindex-thesis-draft.md`, `openappindex-working-paper-draft.md`
      and `.claude/launch.json` at the repo root. If those should not get a DOI, untrack them
      or mark them `export-ignore` in a `.gitattributes` before the release.

## 1. Create an ORCID iD (10 min)

1. Register at <https://orcid.org/register> (name: Tim Meyerdierks; email of your choice).
2. Verify the email. Set name and "Employment/Affiliation" as you want them shown.
3. Note the iD (`0000-000X-XXXX-XXXX`).

## 2. Put the ORCID into the files (5 min)

- `CITATION.cff`: uncomment both `# orcid:` lines and insert
  `"https://orcid.org/<your iD>"`.
- `.zenodo.json` and `publish/zenodo-paper.json`: replace
  `PLACEHOLDER-ORCID-0000-0000-0000-0000` with the bare iD (no URL).
- Check nothing is left that Zenodo would reject:

  ```bash
  cd /Users/timmeyerdierks/Claude/BAS
  grep -n "PLACEHOLDER-ORCID" .zenodo.json CITATION.cff   # must print nothing
  python3 -m json.tool .zenodo.json > /dev/null && echo "json ok"
  ```

  A placeholder still in `.zenodo.json` makes Zenodo's import of the release fail.

## 3. Connect the GitHub repository to Zenodo (10 min)

1. Go to <https://zenodo.org> and click **Log in** → **Log in with GitHub**. Approve the OAuth
   permissions Zenodo asks for (you decide; it needs read access to repositories and webhooks).
2. Optional: under your Zenodo profile → **Linked accounts**, also link ORCID.
3. Profile menu → **GitHub** → **Sync now**.
4. Find `tim-muky/openappindex` and switch its toggle **on**. Refresh the page and check it is
   listed as enabled.

The repository is public (checked 2026-10-05), and Zenodo reads `.zenodo.json` (it ignores
`CITATION.cff` when both exist).

## 4. Make a release to mint the DOI (15 min, plus a few minutes' wait)

`.zenodo.json` must be on the commit you tag, so the files have to be on `main` first (commit
and merge the bundle branch the usual way). Then:

```bash
cd /Users/timmeyerdierks/Claude/BAS
git checkout main && git pull
gh release create v0.1.0 --target main \
  --title "openAPPindex v0.1.0 — cooking and sleep datasets, working paper draft v0.1" \
  --notes "Dataset (CC BY 4.0) and code (AGPL-3.0) behind the working paper draft v0.1. Corrections: korrektur@openappindex.org"
```

(Or on github.com: **Releases** → **Draft a new release** → tag `v0.1.0` → **Publish
release**. A release left as a draft is not archived.)

Then on Zenodo → profile menu → **GitHub**: the release appears with a DOI badge within a few
minutes. Open the record and note **two** DOIs:

- the **concept DOI** ("Cite all versions") — use this one everywhere below;
- the version DOI for v0.1.0.

Check the record page: title, author with ORCID, licence CC BY 4.0, the description's licence
paragraph.

## 5. Write the DOI back into the repository (10 min)

- `CITATION.cff`: uncomment the top-level `# doi:` line, insert the concept DOI.
- `publish/huggingface/README.md`: replace `PLACEHOLDER — Zenodo concept DOI…` and the
  `DOI: PLACEHOLDER` in the BibTeX.
- `publish/zenodo-paper.json`: replace the `PLACEHOLDER-10.5281/zenodo.XXXXXXX` identifier.
- Optional: add the Zenodo DOI badge (copy it from the record page) to `README.md`.
- Validate and commit:

  ```bash
  pipx run cffconvert --validate -i CITATION.cff     # or: pip install cffconvert
  ```

## 6. Zenodo record for the paper (25 min)

1. Make a PDF of the paper: open <https://openappindex.org/paper.html> in a browser →
   **Print** → **Save as PDF** (`openappindex-working-paper-v0.1.pdf`). Read it once.
2. Zenodo → **New upload**. Upload the PDF.
3. Fill the form from `publish/zenodo-paper.json`: resource type *Publication → Working
   paper*, title, creator with ORCID, description (the abstract, verbatim), licence,
   keywords, the three related identifiers. Use **Reserve DOI** if you want the DOI before
   publishing.
4. **Publish.** Put the paper's DOI into `CITATION.cff` (`preferred-citation` → `# doi:` line).

## 7. Hugging Face account, organisation and token (15 min)

1. Create an account at <https://huggingface.co/join>, verify the email.
2. Create the organisation at <https://huggingface.co/organizations/new>
   (suggested name: `openappindex`).
3. Create an access token at <https://huggingface.co/settings/tokens> with **write** access
   (fine-grained: write to `openappindex` repos only). Do not paste it into chat or into a
   file in the repository.
4. Install the CLI and log in:

   ```bash
   brew install hf                 # or: pip install -U huggingface_hub
   hf auth login                   # paste the token when asked
   hf auth whoami                  # should show your user and the openappindex org
   ```

## 8. Create the dataset repo and upload (20 min)

The card's subsets expect this layout in the Hugging Face repo:
`README.md`, `cooking/corpus_de.json`, `cooking/closure_apps.json`, `cooking/prices_de.json`,
`cooking/corrections.json`, `cooking/snapshots/`, `cooking/changelog/`. The gate-experiment
files stay on GitHub/Zenodo only.

```bash
cd /Users/timmeyerdierks/Claude/BAS
REPO=openappindex/app-store-de          # your choice of name

# stage exactly the files the card describes
rm -rf /tmp/hf-stage && mkdir -p /tmp/hf-stage/cooking
cp publish/huggingface/README.md /tmp/hf-stage/README.md
cp sample/data/public/{corpus_de.json,closure_apps.json,prices_de.json,corrections.json} /tmp/hf-stage/cooking/
cp -R sample/data/public/snapshots sample/data/public/changelog /tmp/hf-stage/cooking/

hf repos create "$REPO" --repo-type dataset
hf upload "$REPO" /tmp/hf-stage . --repo-type dataset \
  --commit-message "openAPPindex cooking dataset, card v0.1"
```

Then open `https://huggingface.co/datasets/$REPO`:

- the Dataset Viewer shows four subsets: `cooking_sweep`, `cooking_closure`,
  `cooking_prices`, `corrections` (all four were test-loaded locally with `datasets` on
  2026-10-05);
- the card renders, licence shows CC BY 4.0;
- optionally add the HF URL to the Zenodo record (new version) and to `README.md`.

## 9. The sleep dataset (exported 2026-10-05; upload together with §8)

1. Fill in the `TODO (sleep)` blocks in `publish/huggingface/README.md` with the real file
   names from the export (one subset per file).
2. Upload:

   ```bash
   hf upload "$REPO" sleep/data/public sleep --repo-type dataset \
     --commit-message "Add sleep and meditation dataset"
   hf upload "$REPO" publish/huggingface/README.md README.md --repo-type dataset \
     --commit-message "Card: sleep subsets"
   ```

3. A new GitHub release (`v0.1.1` or similar) creates a new Zenodo version under the same
   concept DOI.
