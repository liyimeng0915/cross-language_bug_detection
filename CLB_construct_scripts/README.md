## CLB Dataset Construction Scripts

This project provides a set of semi-automated scripts for constructing a Cross-Language Bug (CLB) dataset, aiming to systematically collect, filter, and curate cross-language bug–related data from open-source multilingual software projects hosted on GitHub.

### Overview

The dataset construction process follows a stage-wise, semi-automated workflow. Each script depends on the output of the previous step, and manual inspection and filtering are performed after each stage to improve data quality and reliability.
 All scripts are designed to be extensible and can be customized or modified to accommodate specific research requirements.

The file `myconfig.py` serves as a global configuration file, where common parameters (e.g., directory paths) can be specified. Other task-specific parameters should be manually configured in the `main` function of each script. Each script can be executed independently by running its corresponding `main` function.

------

### Dataset Construction Pipeline

#### 0. GitHub Repository Selection

In `0_getRepo.py`, repository selection criteria (e.g., programming language combinations, number of stars) can be configured. Running this script produces a list of GitHub repositories that satisfy the specified conditions.

#### 1. Repository List Preprocessing

The script `1_repo_process.py` is used to preprocess the repository list obtained in the previous step. This includes:

- Removing duplicate repositories;
- Performing basic statistical analysis;
- Manually reviewing repository descriptions to further filter out projects that do not align with the research objectives.

#### 2. Issue Processing

For each selected repository, relevant GitHub Issues are collected and filtered based on predefined criteria, such as:

- Issue labels;
- Issue status (e.g., open or closed);
- Other metadata as required by the study.

#### 3. Commit Collection

All commit records of the selected repositories are retrieved to support subsequent bug localization and repair analysis.

#### 4. Issue number Extarct from Commit 

Issue numbers are extracted from commit messages to establish associations between commits and issues, enabling the identification of commits that correspond to issue-fixing activities.

#### 5. Commit Filtering and Linking

Based on the extracted Issue–Commit mappings, commits are further filtered, and each issue is systematically linked to its corresponding fixing commit(s) within each repository.

#### 6. GitHub Repository Cloning

All selected repositories are cloned to the local environment, providing the source code required for subsequent analysis.

#### 7. Multilingual Code Identification

Cross-language code identification is performed on the cloned repositories to detect multiple programming languages and their interactions.
 Detailed instructions can be found in the `README` file under the `CLCFinder` directory.

#### 8. Result Processing and Dataset Generation

All intermediate results are cleaned, integrated, and post-processed to produce the final Cross-Language Bug (CLB) dataset, which can be directly used for empirical studies and model training.

------

### Notes

- This workflow emphasizes data quality over automation, leveraging manual validation at key stages to reduce noise and mislabeling;
- The scripts are designed to be flexible and extensible, supporting a wide range of research tasks such as cross-language bug detection and repair analysis;
- It is recommended to execute the scripts in the prescribed order to ensure correct data dependencies.