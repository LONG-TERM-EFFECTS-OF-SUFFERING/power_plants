# Power plants

Workshop 2 (_Taller 2: Plantas de energía_) of _Programación por Restricciones_, Universidad del Valle. A power provider's production plan over $n$ days is modeled as a constraint optimization problem (COP), implemented in MiniZinc, tested, and written up in one LaTeX report.

[`statement.pdf`](statement.pdf) is the assignment. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before contributing: it explains the split between the three members, the model everyone builds on, and the rules for AI assistants.

## Members

- Brandon Calderón Prieto (2125974).
- Orlando Alexis Rengifo Mejia (2223878).
- Santiago Nuñez Ramirez (2225625).

## Status

| Part                                                                    | Owner              | Status  |
| ----------------------------------------------------------------------- | ------------------ | ------- |
| Model `PlantaEnergia.mzn`, `Datos.dzn`, experiments in `scr/verificacion/` | Person A (Brandon) | Done    |
| Report: Descripción del problema, Modelo, Detalles de implementación    | Person A (Brandon) | Done    |
| The 10 test instances in `scr/tests/`; report: Pruebas                  | Person B (Santiago) | Done    |
| Search strategies, solver comparison; report: La búsqueda, Análisis, Conclusiones | Person C (Alexis) | Done    |
| Integration: introduction, cross-section consistency, delivery zip      | Person A (Brandon) | Done    |

## Repository layout

```text
.
├── statement.pdf                assignment
├── main.tex                     report entry point: front page + content/
├── preamble.tex                 packages and macros
├── front_page.tex               APA title page: title, authors, course, professor
├── bibliography.bib             references
├── content/                     one .tex file per report section
├── assets/                      images for the report
├── scr/
│   ├── PlantaEnergia.mzn        model
│   ├── Datos.dzn                input format, with the statement's example
│   ├── README.txt               files and how to run them (Spanish, part of the delivery)
│   ├── tests/                   the 10 test instances, PlantaEnergia_NN.dzn
│   ├── results/                 runs on the 10 test instances (Gecode, HiGHS)
│   └── verificacion/            Person A's experiments: scripts, experimentos/, resultados/
├── build/                       LaTeX output (gitignored)
└── dist/                        delivery zip (gitignored)
```

## Requirements

- MiniZinc 2.9 or later, full bundle (includes Gecode, HiGHS and COIN-BC). Tested with MiniZinc 2.9.3, Gecode 6.3.0 and HiGHS 1.9.0.
- Python 3 for the scripts in `scr/verificacion/`.
- A LaTeX distribution with `latexmk`, `biber`, `apa7` and `biblatex-apa`. A full TeX Live install has all of them.
- Optional: VS Code with LaTeX Workshop, which builds, formats and lints on save.

## Running

```sh
# The model. -s prints statistics; a final "==========" means the optimum was proved.
cd scr
minizinc --solver gecode -s PlantaEnergia.mzn Datos.dzn -D "impl=5;strategy=2"
minizinc --solver highs  -s PlantaEnergia.mzn Datos.dzn -D "impl=5;strategy=1"

# The 10 test instances: impl x strategy into a CSV (from scr/; the committed CSVs)
python3 verificacion/correr_experimentos.py results/PlantaEnergia_gecode_base.csv 5 2 tests/*.dzn
python3 verificacion/correr_experimentos.py results/PlantaEnergia_gecode_estrategias.csv 5 1,2,3 tests/*.dzn
python3 verificacion/correr_experimentos.py --solver=highs results/PlantaEnergia_highs.csv 2 1 tests/*.dzn

# The report, from the repository root
latexmk                                 # writes build/main.pdf
grep -E '^!|undefined' build/main.log   # must print nothing
latexmk -C                              # removes the build output
```

`scr/README.txt` lists what `impl` and `strategy` mean and how to repeat every run in the report.

The delivery zip, `dist/2125974-2223878-2225625-Taller2-PPR-2026-II.zip`, follows Taller 1: `readme.txt` (from `scr/README.txt`), `InformeTaller2.pdf` (from `build/main.pdf`) and the contents of `scr/`.

## Open items

- Confirm the interpretation of G with the professor.
- Confirm that groups of three are allowed, and the zip name.
