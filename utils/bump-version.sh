#!/usr/bin/env bash
set -ex

version_file="cloudsplaining/bin/version.py"
# https://github.com/bridgecrewio/checkov/blob/master/.github/workflows/build.yml#L87-L132

git config --local user.email "action@github.com"
git config --local user.name "GitHub Action"
git pull
git fetch --tags
latest_tag=$(git describe --tags `git rev-list --tags --max-count=1`)
echo "latest tag: $latest_tag"
new_tag=$(echo $latest_tag | awk -F. -v a="$1" -v b="$2" -v c="$3" '{printf("%d.%d.%d", $1+a, $2+b , $3+1)}')
echo "new tag: $new_tag"

echo "__version__ = '$new_tag'" > $version_file

git commit -m "Bump to ${new_tag}"  $version_file || echo "No changes to commit"
git push origin
