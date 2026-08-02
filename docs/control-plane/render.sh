#!/usr/bin/env bash
# Regenerate every view from the model of record (workspace.dsl).
# The DSL is authoritative; everything in generated/ is derived and disposable.
#
# Toolchain (installed 2026-07-25, user-local, nothing system-wide changed):
#   Temurin JDK 17  ~/scoop/apps/temurin17-jdk       (structurizr-cli needs class file 61.0)
#   structurizr-cli ~/tools/structurizr               v2025.11.09
#   PlantUML        ~/tools/plantuml/plantuml.jar     v1.2026.6
#   graphviz        already present                   v14.1.0
set -euo pipefail

JAVA="${JAVA17:-$HOME/scoop/apps/temurin17-jdk/current/bin/java}"
SCLI="${STRUCTURIZR_HOME:-$HOME/tools/structurizr}"
PUML="${PLANTUML_JAR:-$HOME/tools/plantuml/plantuml.jar}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cygpath -m "$HERE/workspace.dsl" 2>/dev/null || echo "$HERE/workspace.dsl")"
OUT="$(cygpath -m "$HERE/generated" 2>/dev/null || echo "$HERE/generated")"
mkdir -p "$HERE/generated"

run_cli() { ( cd "$SCLI" && "$JAVA" -cp "lib/*" com.structurizr.cli.StructurizrCliApplication "$@" ); }

echo "== validate =="
run_cli validate -workspace "$WORKSPACE"
echo "   model OK"

echo "== export =="
run_cli export -workspace "$WORKSPACE" -format plantuml/c4plantuml -output "$OUT"
run_cli export -workspace "$WORKSPACE" -format mermaid          -output "$OUT"

echo "== render =="
( cd "$HERE/generated" && "$JAVA" -jar "$PUML" -tsvg -nometadata ./*.puml && "$JAVA" -jar "$PUML" -tpng -nometadata ./*.puml )

echo "== done =="
ls -1 "$HERE/generated"
