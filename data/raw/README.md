# Third-party raw data (not included)

The files in this folder are third-party datasets. They are not redistributed here: their licences differ, and one source (METR's run-level results) has no licence at the commit used. Every derived file that the papers and the engine read is included elsewhere in `data/`, so the papers' checks and the engine run without this folder. It is needed only to rebuild the derived data with `code/data_part2/`.

| Folder | Source | Terms |
|---|---|---|
| `onet_31_0` | O*NET 31.0 Database, USDOL/ETA | CC BY 4.0 |
| `bls_oews_2019`, `_2020`, `_2021`, `_2025`, `bls_soc` | U.S. Bureau of Labor Statistics, OEWS and SOC | U.S. government work, public domain |
| `anthropic_aei` | Anthropic Economic Index, releases of 27 March 2025 and 26 June 2026 | CC BY |
| `aieconindex_r` | Charles Coverdale, github.com/charlescoverdale/aieconindex (R package; read only for the list of releases) | MIT |
| `gpts_are_gpts` | Eloundou, Manning, Mishkin and Rock, github.com/openai/GPTs-are-GPTs | MIT |
| `ms_working_with_ai` | Tomlinson, Jaffe, Wang, Counts and Suri, github.com/microsoft/working-with-ai | CC BY 4.0 |
| `metr_eval_analysis` | Kwa et al. (2025), github.com/METR/eval-analysis-public | no licence file; only fitted summary parameters are used |
| `damodaran_2026` | Aswath Damodaran, NYU Stern industry datasets (January 2026) | publicly posted; cited, not redistributed here |

Exact URLs, versions, retrieval dates and transformations are in `notes/data_sources_part2.md`, and `CHECKSUMS.sha256` lists the SHA-256 of every file as used. See also `engine/NOTICE.md`.
