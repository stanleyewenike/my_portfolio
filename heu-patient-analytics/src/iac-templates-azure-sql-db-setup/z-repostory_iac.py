
# UNFORTUNATELY, I COULD NOT GET THIS SCRIPT TO WORK!! :-(
    
# I TRIED TO CREATE A NEW REPOSITORY ON GITHUB USING THE PYGITHUB LIBRARY, BUT I RAN INTO SOME ISSUES WITH THE AUTHENTICATION. 
# I TRIED TO USE THE GITHUB TOKEN STORED IN THE GITHUB_TOKEN ENVIRONMENT VARIABLE, BUT I WAS STILL GETTING AN AUTHENTICATION ERROR. 
# I BELIEVE THE ISSUE MIGHT BE RELATED TO THE SCOPE OF THE TOKEN OR SOME OTHER CONFIGURATION ISSUE. 
# I WILL CONTINUE TO INVESTIGATE AND TRY TO RESOLVE THE ISSUE. 
# IN THE MEANTIME, I HAVE PROVIDED THE CODE THAT I ATTEMPTED TO USE FOR CREATING THE REPOSITORY ON GITHUB. 
# I APOLOGIZE FOR THE INCONVENIENCE AND WILL UPDATE YOU ONCE I HAVE A WORKING SOLUTION.  
# I EVENTUALLY WENT TOOK THE ALTERNATIVE APPROACH TO CREATING THE REPOSITORY MANUALLY ON GITHUB AND THEN CLONE IT TO MY LOCAL MACHINE.

#-------------------------------------------------------------------------------------------------------------------------------------------


# This script creates a new private repository on GitHub with the specified name and description.
# It also creates essential directories and files for a typical data science project.
# The GitHub token is stored in the GITHUB_TOKEN environment variable.
# The script uses the PyGithub library to interact with the GitHub API.

#-------------------------------------------------------------------------------------------------------------------------------------------

# Import the required libraries

from github import Github
import os

# It's better to use environment variables for sensitive information like tokens
github_token = os.getenv("GITHUB_TOKEN")
repo_name = "NHS-Health-Analytics"
description = "Repository for NHS HEU Data Science Project"

if not github_token:
    raise ValueError("Please set the GITHUB_TOKEN environment variable")

try:
    g = Github(github_token)
    user = g.get_user()
    org = g.get_organization(user.login)
    repo = org.create_repo(repo_name, description=description, private=True)

    # Create essential directories and files
    structure = {
        "data": ["raw", "processed"],
        "notebooks": ["EDA", "modeling"],
        "scripts": ["etl", "visualization", "modeling"],
        "docs": []
    }

    for folder, subfolders in structure.items():
        repo.create_file(f"{folder}/.gitkeep", "Initial commit", "")
        for sub in subfolders:
            repo.create_file(f"{folder}/{sub}/.gitkeep", "Initial commit", "")

    print(f"Repository {repo_name} created successfully!")

except Exception as e:
    print(f"An error occurred: {e}")