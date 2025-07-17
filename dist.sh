#!/usr/bin/env bash

# Legacy dist.sh script - now uses modern release system
# For new releases, use: python3 scripts/release.py --bump patch --message "Your message"

APP="yaplon"
USAGE="Usage: ./dist.sh releasetext

DEPRECATED: This script is deprecated. Use the new release system instead:
  python3 scripts/release.py --bump patch --message \"Your message\"
  python3 scripts/release.py --bump minor --message \"Your message\"  
  python3 scripts/release.py --bump major --message \"Your message\"
  python3 scripts/release.py --version 1.2.3 --message \"Your message\"

For more options: python3 scripts/release.py --help";

if [ $# -ge 1 ]; then
  echo "⚠️  WARNING: This script is deprecated!"
  echo "Please use the new release system instead:"
  echo "  python3 scripts/release.py --bump patch --message \"$1\""
  echo ""
  echo "Continue with legacy release? (y/N)"
  read -r response
  if [[ "$response" != "y" && "$response" != "Y" ]]; then
    echo "Cancelled. Use: python3 scripts/release.py --bump patch --message \"$1\""
    exit 1
  fi

  echo "## Updating publishing tools"
  python3 -m pip install --user --upgrade setuptools wheel pip twine;

  version=$(python3 -c "import $APP; print($APP.__version__)")
  text=$1

  rm -rf dist/*;

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

  # Create git tag
  git tag -a "v$version" -m "$text"
  git push --tags

  generate_post_data()
  {
    cat <<EOF
{
  "tag_name": "v$version",
  "target_commitish": "$branch",
  "name": "v$version",
  "body": "$text",
  "draft": false,
  "prerelease": false
}
EOF
  }

  echo "## Creating release v$version for repo: $repo_full_name branch: $branch"
  if [ -n "$token" ]; then
    curl --data "$(generate_post_data)" "https://api.github.com/repos/$user/$repo/releases?access_token=$token"
  else
    echo "No GitHub token found. Skipping GitHub release creation."
    echo "Use 'gh' CLI or create release manually on GitHub."
  fi

  echo
  echo "## Publishing on https://pypi.org/project/$APP/"
  echo "Enter your pypi.org login and password:"

  python3 -m twine upload --verbose -c "$text" dist/*;
  
  if command -v open &> /dev/null; then
    open "https://pypi.org/project/$APP/";
  elif command -v xdg-open &> /dev/null; then
    xdg-open "https://pypi.org/project/$APP/";
  fi

else
  echo "$USAGE";
fi
