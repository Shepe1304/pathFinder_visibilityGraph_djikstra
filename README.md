# Advanced Pathfinder Visualization

## Overview
Advanced Pathfinder Visualization is a visual application that finds the shortest path between two points on a customizable map. The application uses visibility graphs and Dijkstra's algorithm to determine the optimal path while avoiding obstacles.

## Features
- **Interactive Map Creation**: Create and visualize maps with obstacles
- **Map Duplication**: Duplicate maps to create extended environments
- **Visibility Graph**: Visualize the visibility lines between points
- **Shortest Path Calculation**: Find and display the optimal path between start and goal points
- **Real-time Information**: View details about vertices, edges, visibility lines, shortest distance, and runtime

## How It Works
The application uses the following algorithms and techniques:
1. Visibility graph generation to determine which points are visible to each other
2. Triangle area calculations to determine if lines intersect with obstacles
3. Dijkstra's algorithm with priority queues to find the shortest path
4. Canvas-based visualization to render the map, visibility lines, and paths

## Usage
1. Run the application: `python pathfinder_final5.py`
2. Use the interface to:
   - Generate a map (set repetition count if desired)
   - View the visibility graph
   - Choose start and goal points by clicking on the map
   - Calculate the shortest path
   - View statistics in the information window

## Controls
- Use the sliders to adjust the scale and position of the map
- Click on the map to set start and goal points
- Toggle buttons to show/hide visibility lines and shortest path

## System Requirements
- Python 3.x
- Tkinter (included in standard Python installation)

## Demo
[YouTube Video Demo](https://www.youtube.com/watch?v=7x_PT6ArAWg)

## Future Improvements
- Optimize the visibility graph generation algorithm
- Add support for custom map imports
- Implement alternative pathfinding algorithms for comparison
- Add map saving/loading functionality

## Acknowledgments
This project was developed as part of a school assignment focusing on Python, computational geometry, and pathfinding algorithms.
