# Provenance and preparation record

Prepared and extended on 15 October 2026 from the local `Covid_Twitter_Project` workspace, branch `core-pipeline`, at commit `5874a3ab79cc14abb82d6b41f7296b18e9a5dbe2`. The initial four-notebook selection is preserved; the subsequent addition responds to the request for broader coverage of paper analyses.

## Attribution basis

Edoardo Maggioni described the notebooks as primarily written by him and the standalone scripts as probably, but not uniformly, written with Codex. This is the basis for the four core notebooks. At the subsequent request to broaden coverage, three existing Python files and one pipeline notebook were included in the separate `supporting_analysis` section. The Python files are treated as existing pipeline code of uncertain authorship, probably including Codex assistance, rather than evidence of independently authored programming. It is not a claim that every notebook cell was written without assistance, nor a line-by-line certification of authorship.

The available Git history begins with a bulk baseline import, `355f27f331e245110493656e225e0292c1463310`. Three selected notebooks are byte-identical to their files in that baseline. `Auto_Edgelist_generator.ipynb` first appears in commit `9471cfc` and is absent from that baseline. All four source files are byte-identical to their versions at the current HEAD. These comparisons establish which versions were selected; commit dates, author fields and filenames do not establish who wrote the code or whether earlier AI assistance occurred.

The larger research project is collaborative. BiCM/community-detection notebooks contain a collaborator contact attribution and an adapted reshuffling routine. Their cell-level contribution boundaries remain unresolved, so those mixed-source notebooks are excluded from this selection rather than relabelled. This does not imply that the notebooks as a whole were written by someone else. The selected label-propagation notebook retains its method and library references. No implementation of BiCM, Louvain, Leiden, random-walk sampling or motif classification is attributed to Edoardo here.

## Selection assessment

- `master_analysis_10e6_reverse.ipynb` is the main example: it translates sampled paths into community-level features, conditional tables, persistence measures, profile distances and visual summaries. It is more compact than the longer `master_analysis*` variants and keeps the analysis readable. Its manual labels, repeated input loading and assumptions about string labels and nonempty samples limit portability.
- `Motifs_LabelPropagation.ipynb` shows edge-frequency aggregation, graph construction, identifier alignment and use of an existing partition as fixed labels. The propagation algorithm comes from igraph. Repeated display cells, an expected CSV index column and an undirected graph are retained.
- The two extraction notebooks show complementary preprocessing: preserving retweet events and constructing deduplicated verified–unverified pairs. They are small and concrete, but retain Colab paths, manual date ranges and directory assumptions.

Together they are worth showing as research programming supporting a substantive network-analysis question. They provide evidence of data transformation, graph preparation and analytical Python work. They do not by themselves demonstrate a deployable application, a general-purpose library, implementation of the external algorithms or a fully reproducible pipeline.

Excluded: most of `core_pipeline`, other standalone scripts, the separate `rw_motifs` library, mixed-source BiCM/community-detection notebooks, exploratory/duplicate notebooks, manuscripts, figures and all account-level research data. The explicit exceptions are the six existing files listed below: three Python files, a configuration, one diagnostic notebook and one community-level aggregate input. The later pipeline is not presented as Edoardo's independently authored code. Exclusion is a selection decision, not proof of authorship or AI involvement for every excluded file.

## Changes made by Codex in this preparation

Only notebook copies were sanitised: the four files under `notebooks/` and the additional diagnostic under `supporting_analysis/core_pipeline/notebooks/`. Every cell, its type, position and exact `source` value were preserved, including markdown, comments, original language and empty cells. Original cell IDs and notebook format versions were retained where present.

All saved outputs were replaced with empty lists, execution counts were reset to null, and all cell metadata were cleared. Notebook metadata were replaced with a generic Python 3 kernel descriptor and language name, without a Python version. This removes saved data displays, images, execution history and Colab/editor metadata while retaining the source. Generic Google Drive directory strings embedded in the code remain; they contain no account name or home-directory identity.

Codex wrote and updated `README.md`, this record and `.gitignore`. No code corrections, refactoring, new functions, tests or synthetic examples were introduced. The extension copies existing code and one existing anonymous aggregate table. The existing profile-comparison script was rerun in isolation for verification; its generated outputs are not shipped. The packaging/checking utilities used during preparation are not part of the selection. Original workspace files were not edited. Publication of this prepared selection as a public GitHub repository was explicitly requested by Edoardo on 15 October 2026. The new repository has its own publication history; the original research workspace and its Git history are not included.

## Verification and fingerprints

The checks compare parsed notebooks after removing only the declared metadata, outputs and execution-count fields. All remaining fields match, and the original source-file bytes remain unchanged. Every selected Python code cell parses successfully without executing it. The prepared folder was checked for unexpected files, embedded attachments, credentials, account/contact identifiers and local home-directory paths. No such material was found in the prepared selection; the only retained absolute code paths are the generic Colab/Drive locations described above. No raw/account-level datasets, third-party package distributions or stored notebook outputs are included. The single existing aggregate input contains 11 rows of numerical community labels, shares and motif frequencies, with no account identifiers or individual paths. Scripts and the configuration are byte-identical copies, including unused helper functions and configuration settings.

No notebooks were executed, no large network/path calculations were repeated, and no clean-environment validation was performed. The profile-distance calculation alone was rerun, as detailed below. JSON structure and Python syntax checks are not a full notebook-schema validator or a runtime test.

SHA-256 fingerprints below distinguish the original complete notebook, the sanitised copy, and their identical cell content. For the cell-content hash, serialise `[[cell["cell_type"], cell["source"]] for cell in notebook["cells"]]` using Python `json.dumps` with `ensure_ascii=False` and `separators=(",", ":")`, then hash its UTF-8 bytes. The source value is preserved as stored, without joining or normalising its lines.

### `Auto_Edgelist_generator.ipynb`

12 cells, including 7 code cells.

- Original file: `ab277a305062ff62df0f47b649a9660a86de8dfba83b47dc352f54cbe65db26f`
- Sanitised file: `912e68f1e5352843fd130985d1d8d1e91037277e9278aa7f5dcb1e4d3966d897`
- Shared cell content: `ffe294423cef457761924eaf3be5a3a5b5ed74eec91665a627b9ced031c28eff`

### `FullNet_Auto_Edgelist_generator.ipynb`

10 cells, including 6 code cells.

- Original file: `461b944b386dfa0ea56c10f09a0714950e0a4e0bdd090c7054a0a4179bfaf930`
- Sanitised file: `d137fe15bc6795d4f0465ffb287c2f64c7e3d1bcf108bda17e7dd79319a54e18`
- Shared cell content: `a57eef535863371c3adad16ca45a6b7f333ce0860874c312d3019095ac69f9bc`

### `Motifs_LabelPropagation.ipynb`

18 cells, including 15 code cells.

- Original file: `d0bec73e0a3c28d0dedf537775c07a5756c9f52eebe51e372f039ec4ca0f959b`
- Sanitised file: `f2bb131df1ba69c8fe743f9814c984edb07a07237896171c422d49101e5e5886`
- Shared cell content: `bd884dc200e1d29378229384f70a1f915d2274213b1ac2f970b5d66e8e20e906`

### `master_analysis_10e6_reverse.ipynb`

14 cells, including 13 code cells.

- Original file: `70d5635fd2ba5b4b8be27ceffadfc25cb3c472d4c4ee14d2191165d4caf0307e`
- Sanitised file: `fb4fbdb0f7bf10b2ea86a9b84ad82808d65677f19fa58f5b022db02f9fa6ea88`
- Shared cell content: `94ec1eafb366a22b9807c1e532cc605e454cfb50b1544149152d65bb9d2192bd`

## Additional paper coverage and bounded execution check

- `plot_js_motif_profiles.py` operates on the included existing profile table, corresponding to the paper's motif-distribution-by-starting-community table (ten major communities plus Other). All 11 input rows match the manuscript values, including the starting shares and eight motif frequencies. In an isolated copy, the unchanged script completed and regenerated `js_distance_matrix_attention_top10.csv` and `js_distance_long_attention_top10.csv` byte-for-byte as recorded in the research workspace. It also generated the two PNGs corresponding to the manuscript's community-profile dendrogram and heatmap. The workspace reference images match the canonical manuscript assets, but the regenerated PNGs do not: the dendrogram has the same dimensions with different pixels, and the heatmap dimensions differ. Numerical correspondence is verified; pixel-identical image reproduction is not.
- `plot_lwcc_degree_strength_distributions.py` produces four filenames referenced in the manuscript appendix: `lwcc_in_degree_distribution.png`, `lwcc_out_degree_distribution.png`, `lwcc_in_strength_distribution.png` and `lwcc_out_strength_distribution.png`. It requires the original weighted LWCC edge list. It was not executed and its numerical agreement with those appendix figures is unverified.
- `prob_to_sink_eq1_fractions.ipynb` adds a related absorption diagnostic for both orientations. It uses an untruncated strength-imbalance ratio and `numpy.isclose` to one, so it should not be described as a general sink-probability implementation or an exact-equality count. No match to a particular reported numerical result is claimed. It requires the weighted LWCC edge list and was not executed.
- `rw_common.py` is included intact to satisfy imports, preserving the original code. It also contains theoretical-probability, motif-classification and sampling helpers not exercised by this check. These follow the wider project's random-walk framework, attributed in the manuscript to Picciolo, Ruzzenenti, Holme and Mastrandrea (2022); no novelty or independent authorship is claimed. Only a small subset of the module is used by the added scripts.
- `config.yaml` is an unchanged existing configuration, not a newly designed environment or pipeline. It includes unrelated settings and historical expected counts for excluded stages. The only input copied is the anonymous community-profile table; neither tweet data nor node-level network data have been added.

The small check used the already available local Python 3.13 environment with NumPy, pandas, Matplotlib and SciPy. No package versions were inferred as the original research requirements, and no environment was installed or pinned. The program ran on an isolated copy outside the prepared folder, with all generated tables, figures and path-containing manifests left outside the deliverable. The raw records and upstream sampling were not revalidated.

### Fingerprints of the additions

The original and prepared hashes are identical for Python files, configuration and the aggregate CSV. The diagnostic notebook differs only by the declared output/metadata cleanup. Matching HEAD indicates a recorded version, not authorship.

- `supporting_analysis/core_pipeline/src/plot_js_motif_profiles.py` (matches HEAD byte-for-byte)
  - Original SHA-256: `1c432dbe6a403786f814e0e6dd14a0f591f884bec1bbc5c354c0ad984fdeb8b0`
  - Prepared SHA-256: `1c432dbe6a403786f814e0e6dd14a0f591f884bec1bbc5c354c0ad984fdeb8b0`

- `supporting_analysis/core_pipeline/src/plot_lwcc_degree_strength_distributions.py` (matches HEAD byte-for-byte)
  - Original SHA-256: `f5f4b8f0d08fd74685160bb21464be44a228dd6bc33a7e9daf500892f09d54f3`
  - Prepared SHA-256: `f5f4b8f0d08fd74685160bb21464be44a228dd6bc33a7e9daf500892f09d54f3`

- `supporting_analysis/core_pipeline/src/rw_common.py` (matches HEAD byte-for-byte)
  - Original SHA-256: `ea5e9c459e21b4577236a6228415e498fc39e39bf183c35a2318d211aee4719b`
  - Prepared SHA-256: `ea5e9c459e21b4577236a6228415e498fc39e39bf183c35a2318d211aee4719b`

- `supporting_analysis/core_pipeline/configs/config.yaml` (matches HEAD byte-for-byte)
  - Original SHA-256: `acb54f26d0b1c71d5d1fa2450d503a0f7529aeb5047d8b463fbbe983ea8168e1`
  - Prepared SHA-256: `acb54f26d0b1c71d5d1fa2450d503a0f7529aeb5047d8b463fbbe983ea8168e1`

- `supporting_analysis/core_pipeline/outputs/runs/2prat/09_aggregations/top10/motifs_by_start_comm_attention_top10.csv` (not confirmed against HEAD)
  - Original SHA-256: `8f3a185eef96566ab8f499ccf449b0e5900e7aa7bec6cc65fccfa71e9b169a34`
  - Prepared SHA-256: `8f3a185eef96566ab8f499ccf449b0e5900e7aa7bec6cc65fccfa71e9b169a34`

- `supporting_analysis/core_pipeline/notebooks/prob_to_sink_eq1_fractions.ipynb` (matches HEAD byte-for-byte)
  - Original SHA-256: `9ff50c7977d432d5fce1426f5e731d319e8584b175e0ac1d4002af15dab6b25c`
  - Prepared SHA-256: `cd24e9953fd0a26d65198cf789b79c817b7fffc11e8bd565c71153220555193c`
  - Preserved cells: 5, including 3 code cells.

## Attribution and reuse limitations

Authorship is documented at the level supported by Edoardo's description and the local evidence. Any stronger claim about unassisted or exclusive authorship would require further confirmation. No licence has been chosen, and permission to relicense collaborative material has not been established by these checks. No account-level data redistribution rights were assessed, because those data are excluded. The one included aggregate table contains only the community-level values already present in the manuscript; this is a content/provenance check, not a legal assessment of all collaborative research materials. Apart from the bounded profile-comparison check, execution requires the missing research inputs and the original configuration, as detailed in the README.
