#!/usr/bin/env bash

APP="yaplon"
USAGE="Usage: ./dist.sh releasetext";
if [ $# -ge 1 ]; then

  echo "## Updating publishing tools"

  python3 -m pip install --user --upgrade setuptools wheel pip twine;

  version=$(echo -e "import $APP.__init__\nprint($APP.__init__.__version__)" | python3)

  text=$1

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
  echo "## Publishing on https://pypi.org/project/$APP/"
  echo "Enter your pypi.org login and password:"

  python3 -m twine upload --verbose -c "$text" dist/*;
  open "https://pypi.org/project/$APP/";

else
  echo $USAGE;
fi
