---
title: Code Recipe Template
permalink: /code-recipes/template/
description: Standardized structure and checklist for creating new Delta Lake or Apache Iceberg recipes.
---

# Recipe Template

Use this template when creating a new code recipe. Copy this entire directory structure and customize it for your use case.

## Directory Structure

```
recipe-name/
├── problem.md          # Problem description (required)
├── solution.py         # Python solution (required for Python recipes)
├── solution.sql        # SQL solution (optional, or instead of .py)
├── requirements.txt    # Python dependencies (required for Python recipes)
├── environment.yml     # Conda environment (optional)
├── validate.sh         # Validation script (required)
└── README.md           # Recipe overview (required)
```

## File Templates

### problem.md

```markdown
# Problem: [Brief Title]

## Use Case
[Describe the real-world scenario where this solution applies]

## Context
[Provide background information about the problem]

## Requirements
- Requirement 1
- Requirement 2
- Requirement 3

## Expected Outcome
[What should happen after applying this solution?]

## Real-World Applications
- Application 1
- Application 2
```

### solution.py

```python
"""
Recipe: [Recipe Name]
Purpose: [Brief description]
Author: [Your Name or GitHub username]
Date: [YYYY-MM-DD]
"""

# Import statements with comments
import relevant_library

def main():
    """
    Main function demonstrating the solution.
    
    Steps:
    1. Step one
    2. Step two
    3. Step three
    """
    # Implementation with clear comments
    pass

if __name__ == "__main__":
    main()
```

### requirements.txt

```
# Python dependencies for [Recipe Name]
# Install with: pip install -r requirements.txt

package-name>=version
another-package>=version
```

### validate.sh

```bash
#!/bin/bash
# Validation script for [Recipe Name]

set -e  # Exit on error

echo "========================================="
echo "🧪 Validating [Recipe Name]"
echo "========================================="

# Install dependencies
pip install -q -r requirements.txt

# Run the solution
python solution.py

# Validation checks
# Add your validation logic here

echo "✅ Validation successful!"
```

### README.md

```markdown
# [Recipe Name]

## Overview
[Brief description of what this recipe does]

## What You'll Learn
- Learning point 1
- Learning point 2
- Learning point 3

## Prerequisites
- Prerequisite 1
- Prerequisite 2

## Quick Start

\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Run the solution
python solution.py

# Validate
./validate.sh
\`\`\`

## Key Concepts Demonstrated
[Explain the key concepts]

## Next Steps
[Suggest related recipes or advanced topics]
```

## Checklist Before Submitting

Before submitting your recipe as a pull request, ensure:

- [ ] All required files are present
- [ ] Code is properly commented
- [ ] `validate.sh` runs successfully
- [ ] Code follows style guides (black, flake8 for Python)
- [ ] README is clear and comprehensive
- [ ] problem.md clearly explains the use case
- [ ] Dependencies are specified correctly
- [ ] No hardcoded secrets or credentials
- [ ] Architecture diagram included (if complex)
- [ ] Tested on clean environment

## Tips for Great Recipes

1. **Be Specific**: Address a concrete problem
2. **Be Clear**: Use comments and clear variable names
3. **Be Complete**: Include all necessary setup steps
4. **Be Tested**: Ensure validation passes
5. **Be Didactic**: Explain not just how, but why
6. **Be Current**: Use latest best practices
7. **Be Safe**: Never commit secrets

## Getting Help

If you need help creating a recipe:
- Check existing recipes for examples
- Ask in [Discussions](https://github.com/Analytical-Guide/Datalake-Guide/discussions)
- Read the [Contributing Guide](../CONTRIBUTING.md)

## Recognition

Great recipes earn points in our gamification system:
- **Merged Recipe PR**: 25 points
- **Recipe Improvement**: 10 points

Your contribution helps the entire data engineering community!
