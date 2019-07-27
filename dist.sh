#!/usr/bin/env bash

USAGE="Usage: ./dist.sh version releasetext";
if [ $# -ge 2 ]; then

  echo "## Updating publishing tools"

  python3 -m pip install --user --upgrade setuptools wheel pip twine;
  version=$1
  text=$2

  rm dist/*;

  echo "## Preparing release"
  python3 setup.py sdist bdist_wheel;

  echo "## Pushing to Github"
  git add --all
  git commit -am "v$version: $text"
  git pull
  git push

  branch=$(git rev-parse --abbrev-ref HEAD)
  token=$(git config --global github.token)

  repo_full_name=$(git config --get remote.origin.url)
  url=$repo_full_name
  re="^(https|git)(:\/\/|@)([^\/:]+)[\/:]([^\/:]+)\/(.+).git$"
  if [[ $url =~ $re ]]; then
    protocol=${BASH_REMATCH[1]}
    separator=${BASH_REMATCH[2]}
    hostname=${BASH_REMATCH[3]}
    user=${BASH_REMATCH[4]}
    repo=${BASH_REMATCH[5]}
  fi

  generate_post_data()
  {
    cat <<EOF
{
  "tag_name": "$version",
  "target_commitish": "$branch",
  "name": "$version",
  "body": "$text",
  "draft": false,
  "prerelease": false
}
EOF
  }

  echo "## Creating release $version for repo: $repo_full_name branch: $branch"
  curl --data "$(generate_post_data)" "https://api.github.com/repos/$user/$repo/releases?access_token=$token"

  echo
  echo "## Publishing on https://pypi.org/project/yaplon/"
  echo "Enter your pypi.org login and password:"

  python3 -m twine upload --verbose -c "$text" dist/*;
  open "https://pypi.org/project/yaplon/";

else
  echo $USAGE;
fi
