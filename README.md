This project aims to analyze trends in the math job market, trends in arxiv publications, and
build a simple regression model to predict math job counts using the arxiv publication counts.

### Installation

```bash
$ conda env create --file=environment.yml
$ conda activate mathjobs
$ jupyter notebook
```

Then download the arxiv publication dataset and unzip it inside the folder $./data/raw$. The directory should look something like this:

```
.
├───data
│   └───raw
│       └───archive
└───notebooks
    └───.ipynb_checkpoints
```

The notebook "./notebooks/1.0-visualize-data.ipynb" contains visualizations of job counts available from
http://web.archive.org/, while the notebook "./notebooks/1.0-job-prediction.ipynb" contains the visualizations of the
linear regression model used to predict math job counts.