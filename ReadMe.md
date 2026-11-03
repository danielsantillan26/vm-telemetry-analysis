
# VM Telemetry Analysis Software
### Version: 1.0
Basic telemetry software developed using Python to visualize Formula SAE car simulation data. Compares up to two vehicle runs simultaneously to determine differences in vehicle and driver performance using different data points. Completed for Virginia Motorsports Software Onboarding, Fall 2026

## Table of Contents
- [General Information](#general-information)
- [Screenshots](#screenshots)
- [Technologies](#technologies)
- [Inspiration](#inspiration)
- [Improvements](#improvements)

## General Information
This project is a simple application that reads University of Virginia Formula SAE car simulation data (transferred as .csv files) and visualizes it in software. The software allows users to pick up to two existing .csv files to read, then select a wide variety of datapoints to examine (e.g., track position, vehicle speed, power draw, etc.). There is also a playbar to scroll through the data as it would play in real time.

The project also has a dummy login/register system serving as a placeholder for the team's in-progress login database.

## Screenshots
<img width="1917" height="1118" alt="image" src="https://github.com/user-attachments/assets/6018a607-2de9-4387-9cc9-27c3eb87e73a" />
<img width="1905" height="1108" alt="image" src="https://github.com/user-attachments/assets/f27d976a-afa4-4a70-b3c9-1839f70304ec" />



## Technologies
This project was fully developed using Python, specifically using the tkinter, matplotlib, pandas, and numpy libraries to visualize the data and build the UI. The dummy login system runs on a local SQLite database with very basic hashing.


## Inspiration
I was inspired by the telemetry systems used in Formula 1 garages and other motorsports to build this project because I have a passion for motorsports. My knowledge of Formula 1 telemetry systems influenced how I designed the UI and gave me context to how I needed to build the software.

## Improvements
This was my first project using Python, so I was relatively new to all the libraries. I used Tkinter for my UI, which can only run on one thread. The drawback with a program like this is the constant need to redraw graphs as someone scrolls through the graphs or as it plays over time, which slows down the program if it runs on one thread. For future iterations of this project, I intend to use PyQT or a similar UI library that implements multithreading to speed up the program.
