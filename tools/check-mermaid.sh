#!/usr/bin/env bash

# Runs mermaid, and composes markdown summary for github action

if [ -z "$GITHUB_STEP_SUMMARY" ]
then
    GITHUB_STEP_SUMMARY=$(mktemp)
fi

declare -i fail=0
WORKFLOW_FILES=$(find . -name '*workflow*.yaml')
AGENT_FILES=$(find . -name '*agents*.yaml')

echo "|Filename|Type|Stats|" >> "$GITHUB_STEP_SUMMARY"
echo "|---|---|---|" >> "$GITHUB_STEP_SUMMARY"

# Generate mermaid for workflows
# TODO Consolidate duplication
for f in $WORKFLOW_FILES
do
    if ! maestro mermaid --verbose "$f"
    then
      RESULT="FAIL ❌"
      fail+=1
    else
      RESULT="PASS ✅"
    fi
    echo "|$f|workflow|$RESULT|" >> "$GITHUB_STEP_SUMMARY"
done

if [ -z "$CI" ];
 then
  cat "$GITHUB_STEP_SUMMARY"
fi

exit $fail
