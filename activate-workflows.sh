#!/bin/bash
# activate-workflows.sh - Activate GitHub Actions workflows

echo "🚀 Activating GitHub Actions workflows..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if workflow templates exist
if [ ! -d "workflows-templates" ]; then
    echo "❌ Error: workflows-templates directory not found"
    exit 1
fi

# Create .github/workflows directory
mkdir -p .github/workflows

# Copy workflow files
echo "📋 Copying workflow files..."
cp workflows-templates/ci.yml .github/workflows/
cp workflows-templates/release.yml .github/workflows/
cp workflows-templates/pr.yml .github/workflows/

echo "✅ Workflow files copied successfully!"

# Check if files were copied
if [ -f ".github/workflows/ci.yml" ] && [ -f ".github/workflows/release.yml" ] && [ -f ".github/workflows/pr.yml" ]; then
    echo "📁 Files created:"
    echo "  - .github/workflows/ci.yml"
    echo "  - .github/workflows/release.yml"
    echo "  - .github/workflows/pr.yml"
else
    echo "❌ Error: Some workflow files were not copied"
    exit 1
fi

echo ""
echo "🔧 Next steps:"
echo "1. Configure repository secrets in GitHub:"
echo "   - PYPI_TOKEN: Your PyPI API token"
echo "   - CODECOV_TOKEN: (Optional) Your Codecov token"
echo ""
echo "2. Push the workflow files to GitHub:"
echo "   git add .github/workflows/"
echo "   git commit -m 'Add GitHub Actions workflows'"
echo "   git push"
echo ""
echo "3. Test the workflows:"
echo "   - Push to master branch (triggers CI)"
echo "   - Create a git tag (triggers release)"
echo "   - Open a pull request (triggers PR workflow)"
echo ""
echo "📖 For detailed setup instructions, see GITHUB_SETUP.md"
echo ""
echo "🎉 GitHub Actions workflows are ready to use!"