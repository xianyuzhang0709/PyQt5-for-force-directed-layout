

# PyQt5 application for force-directed layout

**Force-directed layout algorithms** are intended to visualize the high-dimensional data, which is not scaled well by common visualization techniques. There are four algorithms published:

* **[Brute Force algorithm](https://ieeexplore.ieee.org/document/1173161)**: A basic approach to forced-direct layouts. The force between every pair of nodes is calculated and applied in every iteration. 
  * **Complexity**: O(N^3). 
  * **Note**: This method doesn't show in this application.

* **[Chalmers' 1996 algorithm](https://ieeexplore.ieee.org/document/567787)**: Use random sampling techniques to build up a neighbor set for each node. This method can reduce the computational cost but achieve similar quality results.
  * **Complexity**: O(N^2)

* **[Hybrid Layout algorithm](https://ieeexplore.ieee.org/document/1173161)**: Perform Chalmers' 1996 algorithm on a subset of the data, then the sample layout could be used for interpolating the remaining data-points. 
  * **Stage**: Sampling; Interpolate remainder (First substage: find parent in the sample for each remaining object; Second substage: position remaining objects); Refine.
  * **Complexity**: O(N^(3/2))
  
* **[Pivot Layout algorithm](https://ieeexplore.ieee.org/document/1249012)**: Chose a random sample set (named Pivot set) as an initial sample layout, and pre-calculate the high-dimensional distance from each pivot to all other sample nodes. It is a faster mean of achieving the stage of interpolation. 
  * **Stage**: Sampling; Interpolate remainder; Refine.
  * **Complexity**: O(N^(5/4))

# Setup

Download the project from github:

~~~~bash
git clone https://github.com/xianyuzhang0709/force-directed-layout-algorithms.git
~~~~

Deploy python virtual environment:

```bash
python -m venv env
source env/bin/activate
```

Install necessary packages:

~~~~bash
pip install -r requirements.txt
~~~~

Run:

```bash
cd PyQt5-for-force-directed-layout
python3 app.py
```

# Questionnaire

Please fulfill these questions and leave any comments here, thanks! [Link](https://forms.office.com/Pages/ResponsePage.aspx?id=KVxybjp2UE-B8i4lTwEzyDkRjMxAReNKrp8pePRTom9UNDM2VlYwWEtFUUk1TzJIR0hOSzAyVk9NQS4u)



