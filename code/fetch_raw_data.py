#!/usr/bin/env python3
# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at
# your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
"""Fetch and verify the third-party raw data in data/raw/, which the repository does not redistribute.

Every file is checked against data/raw/CHECKSUMS.sha256 (sha256, path relative to data/raw, bytes), the record of the
files as used. Sources, versions, retrieval dates and transformations: data/raw/README.md and notes/data_sources_part2.md.

    python3 code/fetch_raw_data.py                    fetch every missing file of every source, then verify all
    python3 code/fetch_raw_data.py SOURCE ...         the same for some sources (folder names; --list shows them)
    python3 code/fetch_raw_data.py --check [SOURCE ...]
                                                      verify only: offline, writes nothing (code/regenerate_all.sh)
    python3 code/fetch_raw_data.py --from-dir ~/Downloads [SOURCE ...]
                                                      first take missing files from a folder of files saved by hand
                                                      (for example in a browser), verified before they are copied
    python3 code/fetch_raw_data.py --list             the sources, their URLs and the stages that read them

Options: --no-download (with --from-dir: no network), --user-agent TEXT (sent with every request; bls.gov answers some
scripts only when it names a person and an e-mail address), --strict (also fail on files no script reads), --raw-dir DIR
(another target folder; the checksums still come from data/raw/CHECKSUMS.sha256 unless --checksums), --quiet.

Rules. A file that is present and matches its checksum is never touched. A present file that differs is reported and
left as it is (move it away to fetch the recorded version). A download is written to a hidden temporary file beside its
target and renamed into place only if its sha256 matches; otherwise it is deleted and reported. No credentials are
needed: every source is public. GitHub repositories are read at the recorded commit, file by file, from
raw.githubusercontent.com. The O*NET CSV files are converted from the MySQL archive by the repository's own
code/data_part2/00_onet_mysql_to_csv.py, run in a temporary folder with python3 -I, and only the CSV files that are
missing are moved into place. Sources whose hosts refuse scripts, or that were saved from a browser, get printed
instructions. Exit code 0 when every required file of the selected sources is present and verified, 1 otherwise, 2 for
a usage error.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DEFAULT = ROOT / "data" / "raw"
CONVERTER = ROOT / "code" / "data_part2" / "00_onet_mysql_to_csv.py"
HF = "https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/main/"
BLS_OES = "https://www.bls.gov/oes/special-requests/"
DAMODARAN = "https://www.stern.nyu.edu/~adamodar/pc/datasets/"
ONET_TABLES = ["task_statements", "task_ratings", "task_categories", "tasks_to_dwas", "gwas_to_iwas_to_dwas",
               "gwas_to_iwas", "occupation_data", "content_model_reference", "work_context", "work_context_categories",
               "job_zones", "scales_reference", "work_activities", "job_titles"]   # as in 00_onet_mysql_to_csv.py

BLS_MANUAL = ("bls.gov often refuses scripted downloads (HTTP 403). Open each link above in a browser (they are direct "
              "file links; the tables pages are https://www.bls.gov/oes/tables.htm and https://www.bls.gov/soc/), save "
              "the file unchanged under the name shown, and rerun with --from-dir <download folder>; or retry with "
              "--user-agent \"Your Name your.email@example.com\".")

# One entry per folder of data/raw. url: direct download links in order of preference (relative path -> list of URLs).
# needed_by: the stages of code/regenerate_all.sh, and the code/data_part2 scripts, that read the folder.
# optional: files that no script reads (reported, but missing ones do not fail the check unless --strict).
SOURCES = {
    "onet_31_0": dict(
        title="O*NET 31.0 Database (August 2026 release), USDOL/ETA, CC BY 4.0", kind="onet",
        url={"onet_31_0/db_31_0_mysql.zip": ["https://www.onetcenter.org/dl_files/database/db_31_0_mysql.zip"]},
        derived={f"onet_31_0/{t}.csv": "onet_31_0/db_31_0_mysql.zip" for t in ONET_TABLES},
        needed_by="stages backtest (job_zones.csv) and playbook (task_statements.csv); the engine (job_titles.csv, "
                  "occupation_data.csv, shipped with the repository); code/data_part2 (02, 03, 07, 12)",
        manual="Open https://www.onetcenter.org/database.html (older releases are kept in the site's database "
               "archive), download the O*NET 31.0 MySQL archive db_31_0_mysql.zip (13,504,988 bytes) unchanged, save it "
               "in data/raw/onet_31_0/ or pass its folder with --from-dir, and rerun; the CSV files are then converted "
               "from it by code/data_part2/00_onet_mysql_to_csv.py. The per-table CSV and Excel distributions name "
               "their columns differently and do not match the checksums."),
    "bls_oews_2019": dict(
        title="BLS OEWS May 2019, national (hybrid SOC), U.S. government work", kind="files",
        url={"bls_oews_2019/oesm19nat.zip": [BLS_OES + "oesm19nat.zip"]},
        needed_by="stage backtest (pre-period placebo)", manual=BLS_MANUAL),
    "bls_oews_2020": dict(
        title="BLS OEWS May 2020, national (hybrid SOC), U.S. government work", kind="files",
        url={"bls_oews_2020/oesm20nat.zip": [BLS_OES + "oesm20nat.zip"]},
        needed_by="stage backtest (trend control)", manual=BLS_MANUAL),
    "bls_oews_2021": dict(
        title="BLS OEWS May 2021, national industry-specific (NAICS 2017), U.S. government work", kind="files",
        url={"bls_oews_2021/oesm21in4.zip": [BLS_OES + "oesm21in4.zip"]},
        needed_by="stage backtest (occupation x industry test)", manual=BLS_MANUAL),
    "bls_oews_2025": dict(
        title="BLS OEWS May 2025, national and industry-specific, U.S. government work", kind="files",
        url={"bls_oews_2025/oesm25nat.zip": [BLS_OES + "oesm25nat.zip"],
             "bls_oews_2025/oesm25in4.zip": [BLS_OES + "oesm25in4.zip"]},
        needed_by="stage backtest; code/data_part2 (02, 04, 11)", manual=BLS_MANUAL),
    "bls_soc": dict(
        title="BLS SOC 2010 to SOC 2018 crosswalk (November 2017), U.S. government work", kind="files",
        url={"bls_soc/soc_2010_to_2018_crosswalk.xlsx": ["https://www.bls.gov/soc/2018/soc_2010_to_2018_crosswalk.xlsx"]},
        needed_by="stage backtest", manual=BLS_MANUAL),
    "anthropic_aei": dict(
        title="Anthropic Economic Index, releases of 27 Mar 2025 and 26 Jun 2026 (Hugging Face), data CC BY", kind="files",
        url={"anthropic_aei/release_2025_03_27/onet_task_statements.csv": [HF + "release_2025_03_27/onet_task_statements.csv"],
             "anthropic_aei/release_2025_03_27/task_pct_v2.csv": [HF + "release_2025_03_27/task_pct_v2.csv"],
             "anthropic_aei/release_2026_06_26/data/aei_claude_ai_2026-06-26.csv":
                 [HF + "release_2026_06_26/data/aei_claude_ai_2026-06-26.csv"],
             "anthropic_aei/release_2026_06_26/data_documentation.md": [HF + "release_2026_06_26/data_documentation.md"]},
        optional={"anthropic_aei/release_2026_06_26/data_documentation.md",
                  "anthropic_aei/release_2026_06_26/data_documentation_SUMMARY.md"},
        needed_by="code/data_part2 (03); no stage of code/regenerate_all.sh",
        manual="The links are public (no login). The repository records no Hugging Face revision, so the links read the "
               "dataset's main branch; if a file has changed there since 29 Oct 2026 it will not match, and the version "
               "used must be taken from the dataset's history (https://huggingface.co/datasets/Anthropic/EconomicIndex). "
               "data_documentation_SUMMARY.md is a paraphrase the lead author wrote (notes/data_sources_part2.md 2.11); "
               "it cannot be downloaded, and no script reads it or data_documentation.md."),
    "aieconindex_r": dict(
        title="Coverdale, aieconindex R package (MIT), GitHub", kind="github",
        github=("charlescoverdale", "aieconindex", "5967b3487c76f685c63298615fef490582811988"),
        optional="all", needed_by="none (read only for the list of AEI releases; notes/data_sources_part2.md 2.8)"),
    "gpts_are_gpts": dict(
        title="Eloundou, Manning, Mishkin and Rock, GPTs are GPTs (MIT), GitHub", kind="github",
        github=("openai", "GPTs-are-GPTs", "0471612fef3cc22b74fb884d27bff9dbd3770582"),
        needed_by="stage backtest; code/data_part2 (02, 03)"),
    "ms_working_with_ai": dict(
        title="Tomlinson, Jaffe, Wang, Counts and Suri, Working with AI v1.1 (CC BY 4.0), GitHub", kind="github",
        github=("microsoft", "working-with-ai", "550c00c9d1b054ac78b87da3a26165bace334779"),
        needed_by="code/data_part2 (02, 03, 07); no stage of code/regenerate_all.sh"),
    "metr_eval_analysis": dict(
        title="METR eval-analysis-public (no licence file at the commit used), GitHub", kind="github",
        github=("METR", "eval-analysis-public", "52cb829c7a2efb2d659285c4b1768d191d97f8d2"),
        needed_by="stage params (code/data_part2/08_params.py: the two runs.jsonl files); code/data_part2 (06)"),
    "damodaran_2026": dict(
        title="Damodaran, NYU Stern industry datasets, data of January 2026 (no licence stated)", kind="files",
        url={f"damodaran_2026/{n}.xls": [DAMODARAN + f"{n}.xls"] for n in ("margin", "wacc", "roe", "fundgrEB")},
        needed_by="code/data_part2 (11); no stage of code/regenerate_all.sh",
        manual="Damodaran replaces these files every January, so after January 2027 the links above serve a later "
               "vintage that will not match; the January 2026 files (all dated 5 Jan 2026) must then come from the "
               "archived data on his site. roc_html.csv is not a download: it is the HTML table of "
               "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/roc.html saved from a browser on 29 Oct 2026 "
               "(header row as on the page, percentage strings kept, comma-separated, 98 lines); a copy saved by hand "
               "may differ in bytes from the recorded one (notes/data_sources_nonsoftware.md describes its columns)."),
}


def human(n: int) -> str:
    for unit in ("bytes", "kB", "MB", "GB"):
        if n < 1000 or unit == "GB":
            return f"{n:,} {unit}" if unit == "bytes" else f"{n:.1f} {unit}"
        n /= 1000
    return str(n)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_checksums(path: Path) -> dict[str, tuple[str, int]]:
    out = {}
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        m = re.match(r"^([0-9a-f]{64})  (.+)  (\d+)$", line)
        if not m:
            sys.exit(f"{path}:{n}: not a checksum line: {line[:80]}")
        out[m.group(2)] = (m.group(1), int(m.group(3)))
    return out


def source_of(rel: str) -> str:
    return rel.split("/", 1)[0]


def is_optional(rel: str) -> bool:
    opt = SOURCES[source_of(rel)].get("optional") or set()
    return opt == "all" or rel in opt


def status(raw: Path, rel: str, sums) -> str:
    """ok, missing, size (wrong size) or differs (same size, other sha256)."""
    p = raw / rel
    if not p.is_file():
        return "missing"
    sha, size = sums[rel]
    if p.stat().st_size != size:
        return "size"
    return "ok" if sha256_of(p) == sha else "differs"


def urls_for(rel: str) -> list[str]:
    src = SOURCES[source_of(rel)]
    if src["kind"] == "github":
        owner, repo, commit = src["github"]
        inner = rel.split("/repo/", 1)[1]
        return [f"https://raw.githubusercontent.com/{owner}/{repo}/{commit}/{urllib.parse.quote(inner)}"]
    return list((src.get("url") or {}).get(rel, []))


class Fetcher:
    def __init__(self, raw: Path, sums, user_agent: str, timeout: float, quiet: bool):
        self.raw, self.sums, self.ua, self.timeout, self.quiet = raw, sums, user_agent, timeout, quiet
        self.refused_hosts: dict[str, str] = {}      # a host that refused once is not asked again in this run
        self.notes: dict[str, list[str]] = {}

    def note(self, rel: str, msg: str) -> None:
        self.notes.setdefault(source_of(rel), []).append(f"{rel}: {msg}")

    def _install(self, tmp: Path, dest: Path, rel: str, how: str) -> bool:
        sha, size = self.sums[rel]
        got_size, got_sha = tmp.stat().st_size, sha256_of(tmp)
        if got_sha != sha:
            self.note(rel, f"{how} gave a different file ({human(got_size)}, sha256 {got_sha[:16]}..., expected "
                           f"{human(size)}, {sha[:16]}...): not installed")
            return False
        if dest.exists():                            # appeared meanwhile: never overwrite
            self.note(rel, "appeared while fetching; left as it is")
            return False
        os.replace(tmp, dest)
        return True

    def download(self, rel: str) -> bool:
        dest = self.raw / rel
        for url in urls_for(rel):
            host = urllib.parse.urlsplit(url).hostname or ""
            if host in self.refused_hosts:
                self.note(rel, f"not requested: {host} refused an earlier request ({self.refused_hosts[host]})")
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_name(f".{dest.name}.part")
            for attempt in range(3):
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": self.ua})
                    with urllib.request.urlopen(req, timeout=self.timeout) as r, open(tmp, "wb") as fh:
                        shutil.copyfileobj(r, fh, 1 << 20)
                    return self._install(tmp, dest, rel, f"download from {url}")     # file closed and flushed
                except urllib.error.HTTPError as e:
                    msg = f"HTTP {e.code} from {url}"
                    if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                        time.sleep(2 + 3 * attempt)
                        continue
                    if e.code in (401, 403, 407, 451):
                        self.refused_hosts[host] = f"HTTP {e.code}"
                    self.note(rel, msg)
                    break
                except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
                    reason = getattr(e, "reason", e)
                    text = str(reason)
                    if re.search(r"\b(403|407)\b|Forbidden|refused|Tunnel connection failed", text) or attempt == 2:
                        self.refused_hosts[host] = text[:80]
                        self.note(rel, f"could not reach {host}: {text[:160]}")
                        break
                    time.sleep(2 + 3 * attempt)
                finally:
                    if tmp.exists():
                        tmp.unlink()
        return False

    def from_dir(self, rel: str, folder: Path) -> bool:
        inner = rel.split("/", 1)[1]
        cands = [folder / rel, folder / inner]
        if "/repo/" in rel:
            cands.append(folder / rel.split("/repo/", 1)[1])         # a clone or an extracted archive of the repo
        else:
            cands.append(folder / Path(rel).name)                    # a browser's download folder
        sha, size = self.sums[rel]
        for c in cands:
            if c.is_file() and c.stat().st_size == size and sha256_of(c) == sha:
                dest = self.raw / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                tmp = dest.with_name(f".{dest.name}.part")
                try:
                    shutil.copyfile(c, tmp)
                    return self._install(tmp, dest, rel, f"copy of {c}")
                finally:
                    if tmp.exists():
                        tmp.unlink()
        return False

    def convert_onet(self, missing: list[str]) -> int:
        """Run code/data_part2/00_onet_mysql_to_csv.py on the verified archive in a temporary tree; install the missing
        CSV files that match their checksums."""
        archive = self.raw / "onet_31_0" / "db_31_0_mysql.zip"
        n = 0
        with tempfile.TemporaryDirectory(prefix="onet_convert_") as td:
            td = Path(td)
            script = td / "code" / "data_part2" / CONVERTER.name
            script.parent.mkdir(parents=True)
            shutil.copyfile(CONVERTER, script)
            (td / "data" / "raw" / "onet_31_0").mkdir(parents=True)
            shutil.copyfile(archive, td / "data" / "raw" / "onet_31_0" / archive.name)
            r = subprocess.run([sys.executable, "-I", str(script)], cwd=td, capture_output=True, text=True)
            if r.returncode != 0:
                for rel in missing:
                    self.note(rel, f"conversion failed (exit {r.returncode}): {(r.stderr or r.stdout).strip()[-300:]}")
                return 0
            for rel in missing:
                out = td / "data" / "raw" / rel
                if not out.is_file():
                    self.note(rel, "the conversion did not write it")
                    continue
                dest = self.raw / rel
                tmp = dest.with_name(f".{dest.name}.part")
                try:
                    shutil.copyfile(out, tmp)
                    n += self._install(tmp, dest, rel, f"conversion of {archive.name}")
                finally:
                    if tmp.exists():
                        tmp.unlink()
        return n


def report(raw: Path, rels: list[str], sums, strict: bool, quiet: bool) -> tuple[int, dict[str, list[tuple[str, str]]]]:
    """Print the verification by source; return the number of failing files and the problems by source."""
    by_src: dict[str, list[str]] = {}
    for rel in rels:
        by_src.setdefault(source_of(rel), []).append(rel)
    bad, problems = 0, {}
    for src in SOURCES:
        if src not in by_src:
            continue
        sts = [(rel, status(raw, rel, sums)) for rel in by_src[src]]
        n_ok = sum(s == "ok" for _, s in sts)
        probs = [(rel, s) for rel, s in sts if s != "ok"]
        req_bad = [(rel, s) for rel, s in probs if strict or not is_optional(rel)]
        bad += len(req_bad)
        if probs:
            problems[src] = probs
        if quiet and not req_bad:
            continue
        tag = "verified" if not probs else ("FAILED" if req_bad else "verified (optional files missing)")
        print(f"  {src:<20} {n_ok:>3}/{len(sts):<3} {tag}")
        for rel, s in probs:
            what = {"missing": "missing", "size": "differs (size)", "differs": "differs (sha256)"}[s]
            opt = "  [optional: no script reads it]" if is_optional(rel) else ""
            print(f"      {what:<17} data/raw/{rel}{opt}")
    return bad, problems


def list_sources(sums) -> None:
    for key, s in SOURCES.items():
        files = sorted(r for r in sums if source_of(r) == key)
        size = sum(sums[r][1] for r in files)
        print(f"{key}  ({len(files)} files, {human(size)})\n    {s['title']}\n    read by: {s['needed_by']}")
        if s["kind"] == "github":
            owner, repo, commit = s["github"]
            print(f"    source: https://github.com/{owner}/{repo} at commit {commit}, files from raw.githubusercontent.com")
        for rel, urls in (s.get("url") or {}).items():
            print(f"    {rel}: {' or '.join(urls)}")
        for rel in sorted(s.get("derived") or {}):
            print(f"    {rel}: converted from {s['derived'][rel]} by code/data_part2/00_onet_mysql_to_csv.py")
        manual = [r for r in files if not urls_for(r) and r not in (s.get("derived") or {})]
        for rel in manual:
            print(f"    {rel}: no download link (see the instructions below)")
        if s.get("manual"):
            print(f"    note: {s['manual']}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__.split("\n\n", 1)[1])
    ap.add_argument("sources", nargs="*", help="folder names in data/raw (default: all)")
    ap.add_argument("--check", action="store_true", help="verify only; no network, no writes")
    ap.add_argument("--from-dir", type=Path, help="take missing files from this folder first (verified)")
    ap.add_argument("--no-download", action="store_true", help="do not use the network")
    ap.add_argument("--list", action="store_true", help="list the sources and exit")
    ap.add_argument("--strict", action="store_true", help="also fail on missing files that no script reads")
    ap.add_argument("--raw-dir", type=Path, default=RAW_DEFAULT, help="target folder (default data/raw)")
    ap.add_argument("--checksums", type=Path, default=RAW_DEFAULT / "CHECKSUMS.sha256")
    ap.add_argument("--user-agent", default=os.environ.get("FETCH_RAW_USER_AGENT", "")
                    or f"rule-of-x replication (code/fetch_raw_data.py; Python-urllib/{sys.version_info[0]}.{sys.version_info[1]})")
    ap.add_argument("--timeout", type=float, default=120.0, help="seconds per request")
    ap.add_argument("--jobs", type=int, default=6, help="parallel downloads from GitHub")
    ap.add_argument("--quiet", action="store_true", help="print only problems")
    a = ap.parse_args(argv)

    sums = read_checksums(a.checksums)
    unknown = sorted({source_of(r) for r in sums} - set(SOURCES))
    if unknown:
        print(f"note: CHECKSUMS.sha256 lists folders this script does not know: {', '.join(unknown)}", file=sys.stderr)
    if a.list:
        list_sources(sums)
        return 0
    sel = a.sources or list(SOURCES)
    bad_sel = [s for s in sel if s not in SOURCES]
    if bad_sel:
        print(f"unknown source(s): {', '.join(bad_sel)}; sources: {', '.join(SOURCES)}", file=sys.stderr)
        return 2
    raw = a.raw_dir.resolve()
    rels = sorted(r for r in sums if source_of(r) in sel)

    if not a.check:
        f = Fetcher(raw, sums, a.user_agent, a.timeout, a.quiet)
        todo = [r for r in rels if not (raw / r).exists()]
        present_bad = [r for r in rels if (raw / r).exists() and status(raw, r, sums) != "ok"]
        for r in present_bad:
            f.note(r, "present but differs from CHECKSUMS.sha256: left as it is (move it away to fetch the recorded version)")
        if a.from_dir:
            took = [r for r in todo if f.from_dir(r, a.from_dir.expanduser().resolve())]
            print(f"from {a.from_dir}: {len(took)} file(s) installed")
            todo = [r for r in todo if r not in took]
        derived = {r for s in sel for r in (SOURCES[s].get("derived") or {})}
        if not a.no_download:
            direct = [r for r in todo if r not in derived and urls_for(r)]
            gh = [r for r in direct if SOURCES[source_of(r)]["kind"] == "github"]
            other = [r for r in direct if r not in gh]
            for r in other:
                if not a.quiet:
                    print(f"downloading data/raw/{r} ({human(sums[r][1])}) ...", flush=True)
                f.download(r)
            if gh:
                if not a.quiet:
                    print(f"downloading {len(gh)} file(s) from GitHub at the recorded commits ...", flush=True)
                with ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
                    list(ex.map(f.download, gh))
        need_conv = [r for r in todo if r in derived and not (raw / r).exists()]
        if need_conv:
            arch = sorted({SOURCES[source_of(r)]["derived"][r] for r in need_conv})
            if all(status(raw, x, sums) == "ok" for x in arch):
                n = f.convert_onet(need_conv)
                print(f"O*NET: {n} of {len(need_conv)} CSV file(s) converted from {', '.join(arch)} and verified")
            else:
                for r in need_conv:
                    f.note(r, f"needs the verified archive {', '.join(arch)} first")
        for src, lines in f.notes.items():
            print(f"{src}:")
            for line in lines:
                print(f"    {line}")
        for r in [r for r in todo if not urls_for(r) and r not in derived and not (raw / r).exists()]:
            if not is_optional(r):
                print(f"    data/raw/{r}: no download link; see the instructions below")

    print(f"verification of {len(rels)} file(s) in {raw} against {a.checksums}:")
    bad, problems = report(raw, rels, sums, a.strict, a.quiet)
    extra = []
    for src in sel:
        d = raw / src
        if d.is_dir():
            for p in d.rglob("*"):
                if p.is_file() and ".git" not in p.relative_to(raw).parts and str(p.relative_to(raw)) not in sums:
                    extra.append(str(p.relative_to(raw)))
    if extra and not a.quiet:
        print(f"  note: {len(extra)} file(s) in these folders are not in CHECKSUMS.sha256 and were not checked "
              f"(for example {', '.join(sorted(extra)[:3])})")
    if bad:
        failing = [s for s, pr in problems.items() if any(a.strict or not is_optional(r) for r, _ in pr)]
        print(f"RESULT: {bad} required file(s) missing or different, in {', '.join(failing)}.")
        print(f"To fetch them:  python3 code/fetch_raw_data.py {' '.join(failing)}")
        for s in failing:
            if SOURCES[s].get("manual"):
                print(f"  {s}: {SOURCES[s]['manual']}")
        return 1
    print("RESULT: every required file is present and matches CHECKSUMS.sha256.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
