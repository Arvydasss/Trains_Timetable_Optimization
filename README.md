# Trains Timetable Conflicts Solutions Optimization

This solution is solving trains timetable conflicts and optimize the solution of it. It uses modified Latvian railways data and prints the trains timetable to a .pdf file. This solutions uses quantum and linear programing.

## Data

Data can be found in data folder, where is locationLinksData.csv file, which contains location links between stations of a latvian railway network and LDZ_timetable.xml file, which contains the modified year timetable of a railway network. The LDZ_timetable_filtered.xml file contains the data of the choosen railway network timetable data.

## How to use it?

### How to create QUBO matrix?

In console write line: **python QUBO_generator.py (problem_number)**

It will generate QUBO_matrix.npz file in files folder.

### How to solve it using quantums?

When QUBO matrix is generated, write line in console:
- For real quantum computing: **python Qfile_solve.py 'quantum' (problem_number) 0 0**

- For simulated quantum computing: **python Qfile_solve.py 'simulated' (problem_number) 2000 240**
  
### How to see all the solutions and timetables?

In console write line: **python solution_analysis.py (console/png)**

It will print all the solutions in console and create train_schedule_linear.pdf, train_schedule_original.pdf, train_schedule_simulated.pdf, train_schedule_quantums.pdf files which contains timetable.
