# COVID-19 Retweet Networks and Community Pathways

How does a retweet network connect online communities, and how do short network paths move within and between them? These Python notebooks and supporting scripts cover selected steps of a research project on Italian COVID-19 Twitter: extracting retweet edges, extending community labels to the wider network, and summarising previously sampled random-walk paths.

The contribution shown here is research programming: transforming nested records into network inputs, aligning node identifiers with community labels, defining path-level summaries, and combining tabular analysis with network methods and visualisation. The underlying community-detection and statistical methods come from the libraries and research described below.

## Included version

This selection contains four core notebooks and a small supporting-analysis section from Edoardo Maggioni's research workspace, prepared and extended on 15 October 2026. Edoardo identifies the notebooks as primarily his own work; detailed attribution and the limits of the available history are recorded in [PROVENANCE.md](PROVENANCE.md).

Notebook cell contents, comments, filenames and cell order are preserved. Saved outputs and execution metadata have been removed. The supporting scripts and configuration are unchanged copies of existing files; their authorship is less certain and likely includes earlier Codex assistance. This is a selection of intermediate analysis notebooks, rather than the current complete pipeline or a release reproducing the manuscript's final results. In particular, the path-analysis notebook uses its existing `10e6` filenames and fixed community labels; these do not establish the settings of the final study.

## Guide to the notebooks

For the most substantial core notebook, start with the last notebook in this table. For a small analysis with included input and verified numerical regeneration, see the supporting section below. The first three explain how network inputs and community labels are handled.

| Notebook | What it contains |
| --- | --- |
| [FullNet_Auto_Edgelist_generator.ipynb](notebooks/FullNet_Auto_Edgelist_generator.ipynb) | Extracts retweeter–original-author pairs from daily JSON records and concatenates daily edge tables. Repeated retweets remain as repeated rows; this notebook does not export a weighted graph. |
| [Auto_Edgelist_generator.ipynb](notebooks/Auto_Edgelist_generator.ipynb) | Selects retweets whose endpoints have different verification flags, puts the verified account first, and deduplicates verified–unverified pairs. The resulting bipartite representation combines both retweet directions. |
| [Motifs_LabelPropagation.ipynb](notebooks/Motifs_LabelPropagation.ipynb) | Counts repeated edges as weights, aligns an existing verified-user partition with graph vertices, fixes the supplied labels, and calls igraph's label-propagation routine. The graph is constructed as undirected. |
| [master_analysis_10e6_reverse.ipynb](notebooks/master_analysis_10e6_reverse.ipynb) | Reads precomputed paths and motif labels; calculates motif profiles, first-step and endpoint transitions, within-community persistence, Jensen–Shannon distances, and hierarchical clustering; exports tables and plots. It does not generate or classify random walks. |

These files describe related stages, but they are not connected automatically. Community reconstruction on the verified-user projection and random-walk sampling are outside this selection. Their outputs must be supplied separately, and the community labels must refer to the same partition as the paths.

## Supporting analyses connected to the paper

The separate [`supporting_analysis/`](supporting_analysis/) directory preserves a small part of the existing `core_pipeline` layout. It extends scientific coverage while keeping the core notebook contribution distinct from existing scripts whose authorship is uncertain and probably includes Codex assistance. No new analytical code was written for this addition.

| Existing file within `supporting_analysis/` | Additional coverage | Verification and inputs |
| --- | --- | --- |
| [`core_pipeline/src/plot_js_motif_profiles.py`](supporting_analysis/core_pipeline/src/plot_js_motif_profiles.py) | Jensen–Shannon distances and average-linkage clustering of the ten major communities plus Other; generates the dendrogram and heatmap used for the paper's community-profile comparison. | The supplied 11-row profile table matches the corresponding manuscript table. Running the unchanged script in an isolated copy regenerated the distance matrix and long-format table byte-for-byte as recorded in the research workspace. PNGs were produced but differ from the manuscript assets in rendering and dimensions. |
| [`core_pipeline/src/plot_lwcc_degree_strength_distributions.py`](supporting_analysis/core_pipeline/src/plot_lwcc_degree_strength_distributions.py) | The four LWCC in/out-degree and in/out-strength distribution plots referenced in the paper's appendix. | Requires the original weighted LWCC edge list, which is not included. Source and syntax checked; this script was not executed during preparation. |
| [`core_pipeline/notebooks/prob_to_sink_eq1_fractions.ipynb`](supporting_analysis/core_pipeline/notebooks/prob_to_sink_eq1_fractions.ipynb) | Supporting absorption diagnostic for both orientations: fractions of nodes with an imbalance ratio close to one, under three different denominators. | Requires the same LWCC edge list. Notebook contents preserved and outputs cleared; not executed. No match to a particular reported numerical result has been established. |

The sole included input is [`motifs_by_start_comm_attention_top10.csv`](supporting_analysis/core_pipeline/outputs/runs/2prat/09_aggregations/top10/motifs_by_start_comm_attention_top10.csv): an existing table of community-level shares and motif frequencies, with community labels `1`–`10` and `0` for Other. It contains no user IDs, handles, tweet text or individual paths. Its values are copied from the workspace, not synthetic examples or newly estimated results. Regenerating distances from this table does not regenerate the upstream walks or establish the correctness of the original sampling.

[`rw_common.py`](supporting_analysis/core_pipeline/src/rw_common.py) is retained in full because the scripts import it. It also contains theoretical-probability and random-walk helper routines that are not exercised by these additions; their inclusion is not a claim of independent authorship, a complete sampling pipeline, or runtime validation. The unchanged [`config.yaml`](supporting_analysis/core_pipeline/configs/config.yaml) preserves the original path layout and also contains settings and expected counts for stages not included here. Those unused settings are not a specification of a complete reproducibility package.

With the imported packages available, run the small profile comparison from the `supporting_analysis` directory:

```sh
python core_pipeline/src/plot_js_motif_profiles.py
```

This writes two distance CSVs and a manifest under `core_pipeline/outputs/runs/2prat/09_aggregations/top10/`, and two PNGs under `core_pipeline/figures/`. Generated files are not bundled. The verification used the existing local Python 3.13 environment; no new environment was installed or validated. Rendering can vary with the environment.

The degree/strength script uses the same configuration and can be run with `python core_pipeline/src/plot_lwcc_degree_strength_distributions.py` after the real LWCC edge list is supplied at the configured path. The diagnostic notebook searches upward for that configuration, so retain its existing directory layout. It computes the untruncated ratio `(in_strength - out_strength) / in_strength` and uses `numpy.isclose(..., 1.0)`; it is not a general implementation of the nonnegative sink-probability formula. Its outputs should be read as this specific diagnostic.

## Methods and external software

- pandas and NumPy support record transformation, identifier alignment and aggregation. Matplotlib and seaborn provide plots. NetworkX is also imported in the original setup cells.
- Label propagation uses the [igraph implementation](https://python.igraph.org/en/main/api/igraph.GraphBase.html#community_label_propagation) of the method of Raghavan, Albert and Kumara (2007), with initial and fixed labels. The algorithm itself is not implemented in these notebooks.
- Profile comparison uses SciPy's [Jensen–Shannon distance](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.jensenshannon.html), followed by [average-linkage hierarchical clustering](https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html). These routines are library implementations.
- The wider research workflow uses a Bipartite Configuration Model projection and Louvain/Leiden community detection upstream. Those stages are not bundled. The random-walk motif framework follows Picciolo, Ruzzenenti, Holme and Mastrandrea, “Weighted network motifs as random walk patterns” (New Journal of Physics, 2022); related routines remain in the unchanged shared helper. These methods are not claimed as original methodological contributions here.

The paths analysed here are generated on an aggregated network. They are not observed temporal retweet chains, and the notebook summaries alone do not establish how individual messages diffused.

## Execution conditions

No Twitter records, user tables, edge lists, node-level community assignments or sampled paths are distributed here. Only the community-level motif-profile table described above is included. The notebooks can be read without their research inputs. Execution of the core notebooks and the additional edge-level analyses requires the corresponding inputs and an appropriate Python environment; it has not been verified in a clean environment. Original dependency versions are not established, so no pinned environment or reproducibility claim is provided.

The imported packages across this selection are pandas, NumPy, NetworkX, Matplotlib, seaborn, python-igraph and SciPy, alongside Python's standard library. PyYAML is optional for the existing configuration readers: the included `.yaml` file is also valid JSON, which the fallback reader accepts. The two extraction notebooks also import `google.colab` and mount Google Drive. Their original setup expects Colab; running them elsewhere requires adapting those cells and the paths in a separate working copy.

| Stage | Required inputs and assumptions |
| --- | --- |
| Edge extraction | Line-delimited daily JSON files named `coronavirus_2020_0{month}_{day}.json`, with `user` and `retweeted_status` objects, user IDs, and—for bipartite extraction—verification flags. Month and day ranges are set manually. The existing filename expressions do not pad single-digit days. |
| Daily-file concatenation | The original Drive directories must exist. The full-network notebook writes daily files under `Edgelists` but reads them from `Edgelists/Full_edgelist`; these locations need to be reconciled in an execution copy. Each wildcard import must see only the intended daily tables. |
| Label propagation | `edgelist_full_final.csv` with `user_id_str` and `retweet_author_id`; `row_communities_Leid.csv` with `Node ID`, `Community` and the exported `Unnamed: 0` column that the notebook drops. Labels are supplied by an upstream analysis. No random seed is set here. |
| Path analysis | Both `paths_motifs_communities_10e6_original.csv` and `paths_motifs_communities_10e6_reversed.csv` are read in the early comparison cell. The subsequent analysis defaults to the reversed file and requires `Path_community` and `Motif`. Community paths must parse as lists with string labels: the notebook compares them with string constants, including sink `"-1"`. |

The notebooks retain manual configuration, exploratory display cells, some unused imports and repeated work. The path analysis loads CSVs into memory, reads the reversed input twice, and assumes a nonempty selected sample with enough communities for clustering. Its fixed community list and `9` label for “Other” must already match the input preparation; this notebook does not create that aggregation. CSV exports are written to the configured directories and can replace files with the same names.

## Preparation and reuse

Codex assisted with inspecting and selecting existing files, writing the documentation, clearing outputs and metadata, and checking source preservation. No new analysis code, functions, tests or demonstration data were written during this preparation. The extension copies existing scripts, a configuration, a diagnostic notebook and one existing aggregate input; only the small profile-comparison calculation was rerun for verification. See [PROVENANCE.md](PROVENANCE.md) for file fingerprints and verification details.

No reuse licence has been selected for this copy. The underlying account-level research inputs are excluded and require a separate access and redistribution assessment. The included community-level summary is documented separately in the provenance record.
