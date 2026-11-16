# Contributing

Workshop 2 (_Taller 2: Plantas de energía_) of _Programación por Restricciones_, Universidad del Valle. [`statement.pdf`](statement.pdf) is the source of truth: §1 defines the problem and what to hand in, §2 what the report must contain, §3 the grading and §4 the delivery.

Taller 2 is **one** exercise: one COP, one `PlantaEnergia.mzn`, one `Datos.dzn` format and 10 instances. It can't be split by exercise like Taller 1, and splitting the model into pieces would put the 25 coherence points at risk. So the work is split by **role**, around a model everyone has to understand.

## The split

The workshop is sized for 18 hours of individual work. With three people, the extra time goes into depth (better instances, real optimality checks, more strategies), not into dividing a small task further. The statement says the exercises are solved individually, and the professor can ask anyone about any part: **everyone must be able to explain the whole model**, not only their own part.

|                              | Person A: model                                                                                                  | Person B: data and tests                                                     | Person C: search and analysis                                                         |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **Who**                      | Brandon                                                                                                          |                                                                              |                                                                                       |
| **Owns**                     | `PlantaEnergia.mzn`; the formal model in the report                                                              | The 10 instances in `tests/`; `run_tests.sh` and its CSV                     | Search annotations (`strategy`); solver comparison; analysis; the delivery `readme.txt` |
| **Main tasks**               | Constraints in formal notation, with justification; any number of plants; regime rule per plant; `assert`s on the data | Instances that make each constraint matter (list below); hand-checked optimum on 2–3 tiny instances | At least 2–3 annotations; compare Gecode with a MIP solver (HiGHS, COIN-BC)           |
| **Redundant and symmetry**   | Write them and prove them                                                                                        | Instances where they matter (repeated plants or clients)                     | Measure their effect                                                                  |
| **Report sections**          | Descripción del problema, Modelo, Detalles de implementación                                                     | Pruebas                                                                      | La búsqueda, Análisis, Conclusiones                                                   |
| **Cross-review**             | Reviews C's analysis                                                                                             | Reviews A's model                                                            | Reviews B's tests, and the whole report for coherence                                 |

Person B's 10 instances must include:

- a case where capacity is short, so the G % minimum is what binds;
- a client whose price is below every production cost, who should get exactly G %;
- a case where the high-regime rule binds;
- 1, 3 and 5 plants;
- a long horizon, to stress the search;
- an infeasible case (the minimum G % exceeds the total capacity on some day).

**Why a MIP solver matters for Person C.** Without the high-regime rule the problem is linear and splits day by day. HiGHS and COIN-BC (both bundled with MiniZinc) prove the optimum quickly, which gives a true reference for the optimality analysis and a sharp comparison: how far Gecode gets with each annotation before the time limit.

**Timeline (3 weeks).**

1. Week 1: A has a model running on B's first small instance. B agrees the `.dzn` format with A on day 1, since it is the interface between them. C sets up `run_tests.sh` and the report skeleton.
2. Week 2: A adds the regime rule for every plant and the redundant and symmetry constraints. B finishes the 10 instances and the optimality checks. C runs the strategies and solvers.
3. Week 3: C runs the final experiment on one machine. Everyone writes their section, then the cross-review.

**Status.** Person A's report text is in `content/01` to `content/03`. The model, `Datos.dzn` and A's experiment scripts (`generar_experimentos.py`, `verificar_optimo.py`, `verificacion/resultados/`) still have to be copied into `scr/power_plants/`.

## The shared contract

These come from Person A's model ([`content/02-model.tex`](content/02-model.tex)) and are already cited in the report. Changing any of them means changing the `.mzn`, the report and every CSV that depends on it, so it goes through Person A.

- **Notation.** Sets $\mathcal{K}$ (plants), $\mathcal{S}$ (clients), $\mathcal{D}$ (days); variables $p_{k,i}$ (production), $e_{s,i}$ (delivery), $a_{k,i}$ (high regime). These replace the names in the first plan (`alto`, `umbral`).
- **Constraint labels.** R1–R5 (problem), RD1–RD4 (dominance), RR1–RR2 (redundant), RS1–RS2 (symmetry). The same labels go in the `.mzn` comments and in the report. Don't renumber them.
- **`Datos.dzn` format.** The fields in Table `tab:plantas-formato`: `nPlantas`, `nClientes`, `nDias`, `nombrePlanta`, `nombreCliente`, `capacidad`, `costo`, `porcentajeAlto`, `diasAltoProhibidos`, `pago`, `demanda`, `G`. Every instance uses exactly these.
- **`impl` 1–5.** Each adds one element to the previous one (Table `tab:plantas-impl`): 1 reified R4, 2 linear R4, 3 + dominance, 4 + redundant, 5 + symmetry breaking.
- **`strategy`.** Person A's text already cites strategy 2 (used in every ablation run) and strategy 3 (finds no solution on the large instances in 60 s). Person C defines the annotations but keeps those numbers, or updates A's text together with A.
- **Interpretation of G.** Each client gets between G % and 100 % of its demand every day, and the profit decides how much. Still to be confirmed with the professor.

## Repository layout

```text
.
├── statement.pdf               assignment
├── main.tex                    report entry point: front page + content/
├── preamble.tex                packages and macros
├── front_page.tex              APA title page: title, authors, course, professor
├── bibliography.bib            references
├── content/                    one .tex file per report section (owners below)
├── assets/                     images for the report
├── scr/power_plants/           PlantaEnergia.mzn, Datos.dzn, tests/, run_tests.sh, results/, verificacion/
└── build/                      LaTeX output (gitignored)
```

| File                            | Report section             | Owner |
| ------------------------------- | -------------------------- | ----- |
| `content/01-problem.tex`        | Descripción del problema   | A     |
| `content/02-model.tex`          | Modelo                     | A     |
| `content/03-implementation.tex` | Detalles de implementación | A     |
| `content/04-search.tex`         | La búsqueda                | C     |
| `content/05-tests.tex`          | Pruebas                    | B     |
| `content/06-analysis.tex`       | Análisis                   | C     |
| `content/07-conclusions.tex`    | Conclusiones               | C     |

## Requirements and running

- MiniZinc 2.9 or later, full bundle (Gecode, HiGHS and COIN-BC included). Tested with MiniZinc 2.9.3 and Gecode 6.3.0.
- Bash for `run_tests.sh`; on Windows, Git Bash or WSL.
- A LaTeX distribution with `latexmk`, `biber`, `apa7` and `biblatex-apa`. A full TeX Live install has all of them.

```sh
cd scr/power_plants
# -s prints statistics; a line "==========" means the optimum was proved
minizinc --solver gecode -s PlantaEnergia.mzn Datos.dzn -D "impl=5;strategy=2"
minizinc --solver highs  -s PlantaEnergia.mzn Datos.dzn -D "impl=5;strategy=2"
minizinc --solver cbc    -s PlantaEnergia.mzn Datos.dzn -D "impl=5;strategy=2"

# Report, from the repository root
latexmk                                 # writes build/main.pdf
grep -E '^!|undefined' build/main.log   # must print nothing
latexmk -C                              # removes the build output
```

## Models

- Start the `.mzn` with a header comment like Taller 1's `kakuro.mzn`: workshop, authors, usage line, and the meaning of each `impl` and `strategy` value. Comments in Spanish.
- `impl` and `strategy` are set from the command line with `-D`.
- Domains are computed per element from the data, as tight as it allows. Validate the data with `assert`.
- Gecode works with integers only: no `float` variables. Decimal data are scaled by a power of 10.
- R4 stays linear from `impl` 2 on. The rubric penalizes constraints conditioned on variable values; the only disjunctions are RD1–RD4, and the report justifies them.

## Tests and results

- Instances are `tests/plantas_NN.dzn`. `Datos.dzn` is the statement's example. Person A's ablation instances (`exp_01`–`exp_10`) are separate and stay in `verificacion/`.
- Start `run_tests.sh` from Taller 1's `scr/kakuro/run_tests.sh`. For a COP it also needs the profit column and a status that tells `optimo` (`==========` in the output) from `sat` (a solution, optimum not proved), `insat` and `timeout`.
- Protocol, as in Taller 1: Gecode, 60 s per run, goal = find the optimum and prove it. Nodes are the main metric because they don't depend on the machine; also report failures, peak depth, solve time, compile time and the best profit found. HiGHS and COIN-BC give the reference optimum.
- Commit the CSVs. Every number in the report must come from a committed CSV or from a run whose command the report describes. The final tables come from one run on one machine.

## Report

- Written in Spanish, as an APA 7 student paper (`apa7` class in `stu` mode). `latexmk` must finish with no errors.
- `\section` is a part of §2 of the statement; `\subsection` a part of it (Parámetros, Variables y dominios…). Constraint labels are bold run-in text: `\textbf{R1 (balance diario).}`.
- APA headings are not numbered: refer to a section by its name ("ver Detalles de implementación"), never by a number.
- Tables: a `table` float with `\caption` and then `\label{tab:plantas-<what>}`, booktabs rules, and `tabularx` with the `L` column for text that wraps. Mention every table in the text as `Tabla~\ref{...}`.
- Math goes inside `$...$` or `\[...\]`. Unicode symbols such as ∈, ≤, × or ᵢ make pdflatex fail.
- Numbers in Spanish format: `13,9~s`, `9\,756\,149`, `0,46~\%`. Code names in `\texttt{}`, with `\_` for underscores.
- Images go in `assets/` and are included by file name.
- Citations: add the entry to `bibliography.bib` and cite with `\parencite{key}` or `\textcite{key}`.
- `apa7` already loads graphicx, booktabs, longtable, caption, float and hyperref. Don't load them again; hyperref options go in `\hypersetup`.

## Grading (statement §3)

| Criterion             | Points | What it asks for                                                                                                                                      |
| --------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Variables             | 10     | Precise meaning and domain for each variable. Parameters are never confused with variables, and domains exclude values known to be impossible.        |
| Constraints           | 15     | Every constraint of the problem, stated formally and independently of the implementation, justified when not obvious. Variable-conditioned constraints only when there is no alternative. |
| Symmetry breaking     | 10     | Which symmetries are broken and how to recover the lost solutions; if there are none, a paragraph explaining why.                                     |
| Redundant constraints | 10     | Why they are redundant and why they prune; if there are none, a paragraph explaining why.                                                             |
| Search strategies     | 15     | At least two annotations besides the default, compared with MiniZinc's statistics (nodes, failures, time).                                            |
| Tests                 | 5      | Enough instances to verify correctness and compare strategies, with results in tables or charts.                                                      |
| Coherence             | 25     | The model, the implementation and the analyses in the report match each other.                                                                       |
| Writing               | 10     | Complete, clear, precise and well presented, with the main analyses and conclusions.                                                                  |

## Working together

- Each person edits only their own files (tables above). Those never conflict.
- `main.tex`, `preamble.tex`, `front_page.tex` and the shared contract change by agreement. Adding entries to `bibliography.bib` is fine.
- Pull before you start (`git pull --rebase`). Before pushing, run `latexmk` and the grep above.
- Commit messages in English with a type prefix, as in Taller 1: `feat:`, `fix:`, `docs:`, `chore:`.
- Cross-review in week 3: the reviewer checks the section against the `.mzn` and the CSVs and lists every mismatch; the owner fixes them.

## Delivery (statement §4)

One member uploads a zip named `PPR-CodEstudiante1-CodEstudiante2` (Taller 1 used `2125974-2223878-2225625-Taller1-PPR-2026-II`) containing:

1. `readme.txt`: every file delivered and how to run the model.
2. The report: `build/main.pdf`, renamed.
3. Every `.mzn` and `.dzn` file.

Build it in `dist/`, which is gitignored. `statement.pdf` is the March 2025 edition: check its deadline, group size and zip name against the current course announcement.

## Open items

- Confirm the interpretation of G with the professor.
- Confirm that groups of three are allowed, and the zip name.
- Copy Person A's model and scripts into `scr/power_plants/`.
- Fill in the names of Persons B and C.

## For AI assistants

Read this whole section before doing anything in this repository.

- **Read first.** `statement.pdf`, this file and `content/02-model.tex`, in that order. The model section is the contract every other part depends on.
- **Your user has to defend the work.** The professor can ask any member about any part, and the exercises are meant to be solved individually. Explain the reasoning behind what you write (why a constraint is redundant, why a strategy should prune) so your user can repeat it without you. Don't hand over work they can't explain.
- **Stay in your user's files.** Find their role in the split and edit only those files. Before touching a shared file or another person's section, stop and say so.
- **Protect coherence (25 points).** Never rename a variable, a constraint label, an `impl` or `strategy` number, or a `Datos.dzn` field. A change to the model is made in `PlantaEnergia.mzn`, `content/02-model.tex` and `content/03-implementation.tex` together, with Person A.
- **Never invent numbers.** Every number in the report comes from a committed CSV or a run you executed; name the command. A run that hits the time limit is reported as a timeout, not as an optimum. Don't estimate, extrapolate or round differently from the CSV.
- **Optimal means proved.** In MiniZinc output, `----------` is a solution and `==========` is a proof of optimality. Don't call a value optimal without the second, or without HiGHS or COIN-BC agreeing.
- **Respect the rubric.** Tight domains, no reification outside `impl` 1, disjunctions only where justified, no floats in the model.
- **Language.** Report, `readme.txt` and code comments in Spanish; `CONTRIBUTING.md`, README and commit messages in English.
- **LaTeX.** pdflatex: no Unicode math symbols, no packages `apa7` already loads, headings referenced by name.
- **Check your work.** `latexmk` plus the grep for the report; `minizinc` or `run_tests.sh` for the model. Report what you ran and what it printed.
- **Keep it small.** Reuse Taller 1's scripts and conventions. Don't add dependencies, frameworks or files nobody asked for.
- **Don't commit** `build/`, `dist/` or anything with personal data.
