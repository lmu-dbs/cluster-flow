# Prototype of the Interactive Clustering Tool for the Cluster Flow Concept

[![Python 3.7](https://img.shields.io/badge/Python-3.7-2d618c?logo=python)](https://docs.python.org/3.7/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

This is the prototypical implementation of the concept proposed in the paper 
```
Cluster Flow - an Advanced Concept for Ensemble-Enabling, Interactive Clustering
Sandra Obermeier, Anna Beer, Florian Wahl, Thomas Seidl
```

## Installation
Create virtualenv
```shell
python3.7 -m venv venv 
source venv/bin/activate
```

Install dependencies
```shell
pip install -U pip setuptools
pip install -U -r requirements.txt
```

Run application
```shell
python interactive_tool.py
``` 
A browser window displaying the user interface will open automatically.

The database ```database.db``` file already contains some example projects. 
If this file is deleted/renamed a new empty database is created automatically after application start.

## Workflow
- Upload dataset (some example datasets are located in ```/example_dataset/```). 
- Create Project for an uploaded dataset
- Execute knn graph creation filter
- Add/Combine filters and visualize the clusterings 

## Config
- ```server_port```: Port where server is running
- ```start_browser```: Whether to automatically start browser




