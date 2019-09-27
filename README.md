## Analysis Repositories

This project analyzes the sensitive information in the repositories of different platforms such as GitHub, Azure DevOps, GitLab, etc.

# Requirements

- Docker
- Git
- Python

# Run

Modify the words file with the keywords to list repositories, otherwise it is done in analysis in all repositories

```
git clone repository

# Modify the words file (optional)

pyhton analysis.py --command1 --commands2      #the command is by type
```

# Help

```
pyhton analysis.py -help
```

configure environment variable according to platform, example for azure: devops

- TOKEN
- AZDEV_ORGANIZATION
- AZDEV_PROJECT_ID

---

# Private repository

```bash
export TOKEN=""

```

---

In the directory report the report is generated

for more information see the help
