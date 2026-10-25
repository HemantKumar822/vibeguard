# Synthetic acceptance corpus

These files are scanner inputs, never executable applications. Every planted credential is fake. The public browser key is a negative credential control in all source variants and all generated web captures.

`labels.json` freezes the selected rule/location/line ground truth. Source and controlled repository acquisition use identical bytes and paths. The website runner constructs a bounded HTML response and headers locally; actual pinned ZAP and Gitleaks workers inspect them. Repository retrieval and website capture are substituted only inside this explicit command, never through an API or production setting. Website unsafe-input, access-check and private-backend categories are unsupported.

“Corrected” and “clean” mean controls for the selected labels, not a claim that ZAP will emit no other passive alerts. The measured run produced additional rules 10015, 10055 and 10109. They remain unexpected occurrences (FP relative to these labels), pending human adjudication. Do not relabel them after observing output to improve metrics. All misses survive incomplete coverage. Undefined precision/recall is null. Matching uses rule plus actual resource plus line and deduplicates overlapping reports.

Run `uv run python scripts/checks/run_acceptance.py --output <sanitized-evidence.json>` from the project root. Exit 1 means an executed check, metric, comparison or cleanup gate failed; exit 0 does not certify release acceptance. `--modes website` supports focused reruns. `--live` additionally observes the two existing authorized public team targets without replacing their transport. Live observations have no accuracy score because no ground-truth labels exist for them.
